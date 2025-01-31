# Tools for ETL / backup and migration

`py extract.py <tablename>` to dump all of a table's records to json.file

`py load.py <dumpfile> <tablename>` to load data from a dumpfile to a table. Dumpfile (and thus the source table) must contain a metadata record for table_version. If target table already contains metadata for table_version, it is used. Otherwise, e.g. for fresh tables, it can be manually specified with `py load.py ... -v {number}`.

`py stats.py <dumpfile>` can be used to inspect e.g. statistics of dumpfiles.

## Registering new tables and versions
All valid tables are defined in `core.py`. Add a tablename to `table_names` to be able to extract and load data.

Although DynamoDB is schemaless itself, our application assumes a certain structure. Sometimes, this structure changes, and a new "table version" needs to be added. In order to enable migrating data from older table versions, an upgrade function needs to be provided:

In `transform.py`:
- add a function that transforms a dump to the next version (e.g. `v2_to_v3`)
  - you might want to implement a function for determining the record kinds for the new version (`kind_v3`)
  - (If you want to use `stats.py` for v3 dumps, this is required.)
- add said function to `UPGRADERS` with the key being the version number of the lower version (`2` in this example)
- in case no transformation is needed, you can simply add `lambda x: x` to `UPGRADERS` (though in this situation it is questionable whether a new version is even needed.)
- `load.py` automatically applies all transformations that are required to migrate data from one version to another.
  - (only upgrades are currently supported, though.)