import unittest
from patala_research_ci.incremental import incremental_count, incremental_share

class IncrementalTests(unittest.TestCase):
    def test_delta_count_matches_full(self):
        old=[{'id':'a','oa':True},{'id':'b','oa':False},{'id':'c','oa':True}]
        new=[{'id':'a','oa':True},{'id':'b','oa':True},{'id':'d','oa':False}]
        r=incremental_count(old,new,lambda x:x['oa'])
        self.assertEqual(r.new_value,sum(x['oa'] for x in new)); self.assertEqual(r.new_value,2)
    def test_share(self):
        old=[{'id':'a','kind':'p','oa':True},{'id':'b','kind':'p','oa':False}]
        new=[{'id':'a','kind':'p','oa':True},{'id':'b','kind':'p','oa':True},{'id':'c','kind':'d','oa':True}]
        r=incremental_share(old,new,lambda x:x['oa'],lambda x:x['kind']=='p')
        self.assertEqual(r['new_share'],1.0)

if __name__=='__main__': unittest.main()
