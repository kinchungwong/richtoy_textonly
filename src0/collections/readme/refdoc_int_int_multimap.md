# IntIntMultimap - Reference Documentation

### Expanded methods view

 - ```cls.__init__()```
 - ```iimm.keys()```
   - returns ```Iterable[int]``` (from ```builtins.dict().keys()```)
 - ```iimm.total```
   - property ```int```
 - ```iimm.clear()```
 - ```iimm.copy()```
 - ```iimm[key]```
   - returns ```_ValueSet```
     - ```if value in vs: ...```
     - ```for value in vs: ...```
     - ```len(vs)```
     - ```vs.add(value)```
     - ```vs.discard(value)```
 - ```iimm.items()```
   - returns ```_PairSetView```
     - ```if (key, value) in psv: ...```
     - ```for key, value in psv: ...```
     - ```len(psv)```
     - ```psv.add((key, value))```
     - ```psv.discard((key, value))```
 - ```iimm.value_sets()```
   - returns ```_DictView```
     - ```dv[key]```
       - returns ```_ValueSet``` (see above)
     - ```for key in dv: ...```
     - ```len(dv)```
     - ```if key in dv: ...```
 - ```for key, value in iimm: ...```
 - ```iimm.add(key, value)```
 - ```iimm.discard(key, value)```
