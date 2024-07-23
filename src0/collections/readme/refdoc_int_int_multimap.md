# IntIntMultimap - Reference Documentation

### About this documentation

**WIP - Work In Progress**

### Terminologies and acronyms

  - IIMM (iimm) = IntIntMultimap
    - *(reads: a multi-map from integers to integers)*
  - KVSM = Keys and Value-Sets Mapping
    - *(reads: a mapping from keys to sets-of-values)*
  - KVPS = Key-Value-Pairs Set
    - *(reads: a set of key-value-pairs)*

### Intuitive expectations for users of IntIntMultimap

Before delving into technical requirements, let's consider a typical programmer's
views on how IntIntMultimap can be (should be) used intuitively.

**Question group 1**

  - What does ```len()``` do? 
    - What number should it return?
  - What does ```for _ in iimm: ...``` do?
    - What is the return type?
    - What would the returned value allow?
  - What does ```iimm[key]``` do?
    - What is the return type?
    - What chained methods should be allowed on the returned object?
  - What should ```__contains__``` do?
    - What argument type(s) should ```if _ in iimm: ...``` support?

### A helpful adage from Python documentation

Source: https://docs.python.org/3/reference/datamodel.html#special-method-names

> When implementing a class that emulates any built-in type, it is important that 
> the emulation only be implemented to the degree that it makes sense for the object 
> being modelled. For example, some sequences may work well with retrieval of 
> individual elements, but extracting a slice may not make sense. 
> 
> (One example of this is the NodeList interface in the W3C’s Document Object Model.)

### (For comparison) Python collections protocols, idioms and invariants

User-defined classes that implement a standard collections protocol are expected to
satisfy all of the protocol's behavioral invariants.

However, even if a user-defined class provides a particular set of members, it may
or may not fully satisfy the behavioral invariants of a particular protocol.
This is the main rationale that, for Standard Collections ABCs, isinstance() checks
are performed with registration or direct subclassing.

https://docs.python.org/3/library/collections.abc.html

### Mapping

***```Mapping``` Implies***

  - ```Mapping```
  - ```Collection```
  - ```Sized```
  - ```Iterable```
  - ```Container```

***```Mapping``` Methods***

  - ```__contains__``` (due to ```Container```, ```Collection```)
  - ```__len__```  (due to ```Sized```, ```Collection```)
  - ```__iter__```  (due to ```Iterable```, ```Collection```)
  - ```__getitem__``` (due to ```Mapping```)

***```Mapping``` Fundamental idioms***

```py
KeyType = TypeVar("KeyType")
ValueType = TypeVar("ValueType")

def mapping_export_idiom(user_defined_mapping: Mapping[KeyType, ValueType], assertions: Assertions) -> Iterable[tuple[KeyType, ValueType]]:
    expected_count = len(user_defined_mapping)  ### via __len__()
    assertions.assertGreaterEqual(expected_count, 0)
    assertions.assertEqual(int(expected_count), expected_count)
    actual_count = 0
    for key in user_defined_mapping:  ### via __iter__()
        actual_count += 1
        assertions.assertIsInstance(key, KeyType)
        assertions.assertTrue(key in user_defined_mapping)  ### via __contains__()
        value = user_defined_mapping[key]  ### via __getitem__()
        assertions.assertIsInstance(value, ValueType)
        yield (key, value)
    assertions.assertEqual(expected_count, actual_count, "A Mapping must provide a length that is equal to actual iteration count.")
```

***```Mapping``` Other idioms.***

All other idioms are optional. Some user-defined classes may implement additional members without 
satisfying the invariants of certain protocols. These classes should, therefore, ***not***
inherit from those protocols for which they do not satisfy.


### Expanded methods view on ```IntIntMultimap```

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
