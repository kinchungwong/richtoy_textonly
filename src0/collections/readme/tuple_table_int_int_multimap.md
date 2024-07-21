# TupleTable and IntIntMultimap (in src0.collections)

### Motivation

In game coding, it is often necessary to represent relations between objects
in a way that is not strictly hierarchical (not composite, not aggregate).

In order to support these use cases, a table-of-tuples facility is needed.

Internally, this facility requires a multimap from integers to integers.

The table-of-tuples (TupleTable) automatically indexes values in the tuple,
and allows object relations to be managed without assuming that related
objects must contain fields that reference each other.

In some cases, a direct reference does not make sense. For example, the set
of "all peer objects of same class that share a specific common attribute
with the current object" is better implemented as a query, rather than as a
set stored on the object itself.

In advanced usage, an object can store the essentials, typically by having
an immutable sub-object of NamedTuple and a mutable sub-object of Dataclass,
a stored reference to a TupleTable (a reference from item to its aggregate
root), member functions to facilitate data entry into TupleTable, and query
mapping functions that delegate to the TupleTable.

### Design of the IntIntMultimap

IntIntMultimap supports the following operation:

 - If ```(k, v1)``` and ```(k, v2)``` are both inserted, it is said that
   both are contained in the multimap.

To avoid inconsistency with Python's own collections protocols,
the IntIntMultimap object does not implement these protocols on itself.
Instead, it provides several views that implement protocols.

 - In key-valueset view, it can be modeled as ```Mapping[Key, Set[Value]]```.

 - In kvp-set view, it can be modeled as ```Iterable[Tuple[Key, Value]]```.

The separation, as well as the decision not to provide an ```__len__()``` method,
is intended to prevent the conflicting expectations on these two views.

### Code implementation of the IntIntMultimap

An initial code draft was proven to be inadequate and inconsistent. Unit test
failures revealed that the two views require different behaviors, and cannot
be implemented on the object itself. Instead, views (proxies) must be used.

To simplify the two-views proof-of-concept, it is decided that the singleton
optimization (for keys that are only mapped to one value, an ```int``` is used
instead of a ```set[int]```) will not be implemented, at least initially.
