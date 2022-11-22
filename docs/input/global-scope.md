# Global Scope

## Description

The global scope of the input file refers to any "top level" option not qualified by
sub categories like `locations` or `weights`. Locations inherit settings from the global scope
if the individual locations did not define or override the options themselves.

## Supported options

* Unique options
    * locations (required)
    * weights
* hierarchical options
    * whitelist
    * blacklist
    * priority
    * timed
