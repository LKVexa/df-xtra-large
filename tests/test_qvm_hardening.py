"""Regression tests against the embedded QUORUM VM; no Java prerequisite."""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
VM=ROOT/'vm/QUORUM_LCTL_MSSL_2.1.0/vm'
spec=importlib.util.spec_from_file_location('qvm_hardened',VM/'toolchain/quorum_vm.py')
qvm=importlib.util.module_from_spec(spec);sys.modules[spec.name]=qvm;spec.loader.exec_module(qvm)


class QVMHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload=qvm.compile_source(VM/'src/CORE.lctlc',VM,False)['payload']
        cls.seed=bytes(range(32))
        cls.public=qvm.ed25519_public(cls.seed).hex()
        cls.trust={'keys':{'test':{'algorithm':'Ed25519','public_key':cls.public,'revoked':False}}}

    def test_valid_signed_execution(self):
        image=qvm.sign_payload(copy.deepcopy(self.payload),self.seed,'test')
        vm=qvm.VM(qvm.verify_image(image,self.trust))
        self.assertEqual(vm.run()['status'],'HALTED')
        self.assertEqual(bytes(vm.output),b'A')

    def test_signature_backends_reject_degenerate_keys(self):
        identity=b'\x01'+bytes(31)
        for backend in (qvm._c_ed25519,None):
            with self.subTest(backend=backend),patch.object(qvm,'_c_ed25519',backend):
                self.assertFalse(qvm.ed25519_verify(identity,b'arbitrary',identity+bytes(32)))
                signature=qvm.ed25519_sign(self.seed,b'valid')
                self.assertTrue(qvm.ed25519_verify(bytes.fromhex(self.public),b'valid',signature))
                self.assertFalse(qvm.ed25519_verify(bytes.fromhex(self.public),b'changed',signature))
                large_s=signature[:32]+qvm.encodeint(qvm.decodeint(signature[32:])+qvm.l)
                self.assertFalse(qvm.ed25519_verify(bytes.fromhex(self.public),b'valid',large_s))

    def test_noncanonical_points_refused(self):
        for encoded in (qvm.encodeint(qvm.q),qvm.encodeint(1+(1<<255)),bytes(32)):
            with self.subTest(encoded=encoded.hex()),self.assertRaises(ValueError):qvm.decodepoint(encoded)

    def test_signed_malformed_instructions_refused(self):
        for ins in (None,{'op':'INVALID'},{'op':'MOVI','dst':True,'imm':1},
                    {'op':'MOVI','dst':0,'imm':[]},{'op':'LOAD','dst':0,'width':-1},
                    {'op':'JMP','target':-1},{'op':'MOV'},{'op':'HALT','mode':[]}):
            payload=copy.deepcopy(self.payload);payload['instructions']=[ins]
            image=qvm.sign_payload(payload,self.seed,'test')
            with self.subTest(ins=ins),self.assertRaises(qvm.VMTrap):qvm.verify_image(image,self.trust)

    def test_resource_metadata_and_capabilities_refused(self):
        for key,value in [('memory_bytes',8192),('program_version',True),('instructions',[]),
                          ('entry',-1),('capabilities',{'memory':[[0,8192]],'services':[]})]:
            payload=copy.deepcopy(self.payload);payload[key]=value
            with self.subTest(key=key),self.assertRaises(qvm.VMTrap):qvm.validate_payload(payload)

    def test_signature_metadata_and_rollback_refused(self):
        image=qvm.sign_payload(copy.deepcopy(self.payload),self.seed,'test')
        for field,value in [('algorithm','none'),('signature','nothex'),('key_id',[])]:
            bad=copy.deepcopy(image);bad['signature'][field]=value
            with self.subTest(field=field),self.assertRaises(qvm.VMTrap):qvm.verify_image(bad,self.trust)
        with self.assertRaises(qvm.VMTrap):qvm.verify_image(image,self.trust,-1)
        with self.assertRaises(qvm.VMTrap):qvm.verify_image(image,self.trust,self.payload['program_version']+1)

    def test_vm_step_bounds_and_entry(self):
        for value in (0,-1,True,qvm.MAX_STEPS_DEFAULT+1):
            with self.subTest(value=value),self.assertRaises(qvm.VMTrap):qvm.VM(self.payload,max_steps=value)
        payload=copy.deepcopy(self.payload);payload['instructions']=[{'op':'JMP','target':0},{'op':'HALT'}];payload['entry']=1
        self.assertEqual(qvm.VM(payload,max_steps=1).run()['status'],'HALTED')

    def test_duplicate_and_nonfinite_json_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'input.json'
            for text in ('{"a":1,"a":2}','{"n":NaN}','{"n":Infinity}'):
                path.write_text(text)
                with self.subTest(text=text),self.assertRaises(ValueError):qvm.load_json(path)
            path.write_bytes(b'1234')
            with self.assertRaises(ValueError):qvm.read_bounded(path,3)

    def test_duplicate_source_arguments_refused(self):
        with self.assertRaises(ValueError):qvm.parse_kv('vm.op=HALT;vm.op=MOVI')

    def test_existing_keys_never_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            private=Path(td)/'private';public=Path(td)/'public'
            private.write_bytes(b'existing')
            args=argparse.Namespace(seed=None,private=str(private),public=str(public))
            with self.assertRaises(FileExistsError):qvm.cmd_keygen(args)
            self.assertEqual(private.read_bytes(),b'existing');self.assertFalse(public.exists())
            private.unlink();public.write_bytes(b'public-existing')
            with self.assertRaises(FileExistsError):qvm.cmd_keygen(args)
            self.assertEqual(public.read_bytes(),b'public-existing')
            self.assertEqual(len(private.read_text().strip()),64)
            if os.name!='nt':self.assertEqual(private.stat().st_mode&0o777,0o600)

    def test_state_generation_uses_authenticated_slots(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);key=b'K'*32
            qvm.save_state_dual(root,{'x':1},key)
            (root/'control.json').write_text('{"active":"arbitrary","generation":999999}')
            qvm.save_state_dual(root,{'x':2},key)
            control=qvm.load_json(root/'control.json');self.assertEqual(control['generation'],2)
            self.assertEqual(qvm.load_state_dual(root,key),{'x':2})
            (root/('slot_'+control['active']+'.json')).write_text('{corrupt')
            self.assertEqual(qvm.load_state_dual(root,key),{'x':1})
            self.assertIsNone(qvm.load_state_dual(root,b'Z'*32))
            with self.assertRaises(ValueError):qvm.save_state_dual(root,{},b'')

    def test_atomic_output_preserves_previous_on_failure(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'out.json';path.write_text('old')
            with patch.object(qvm.os,'replace',side_effect=OSError('injected failure')),self.assertRaises(OSError):qvm.write_json(path,{'new':1})
            self.assertEqual(path.read_text(),'old');self.assertFalse(list(Path(td).glob('.qvm-*')))

    def test_links_and_nonregular_inputs_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);outside=root/'outside';outside.write_text('safe');link=root/'link'
            try:link.symlink_to(outside)
            except OSError:self.skipTest('link privilege unavailable')
            with self.assertRaises(ValueError):qvm.read_bounded(link)
            with self.assertRaises(ValueError):qvm.write_json(link,{'bad':1})
            with self.assertRaises(ValueError):qvm.write_key_new(link,b'bad')
            self.assertEqual(outside.read_text(),'safe')
            if hasattr(os,'mkfifo'):
                fifo=root/'fifo';os.mkfifo(fifo)
                with self.assertRaises(ValueError):qvm.read_bounded(fifo)


if __name__=='__main__':unittest.main()
