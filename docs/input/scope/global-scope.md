# Global Scope

## Description

The global scope of the input file refers to any "top level" option not qualified by
sub categories like `locations` or `weights`. Locations inherit settings from the global scope
if the individual locations did not define or override the options themselves.

## Supported options

* Unique options
    * [`locations`](/input/scope/location-scope) (Required)
        * **Description**: Please see section on the [location scope](/input/scope/location-scope)
for more details.
        * **Type**: List[Location]
        * **Required**: True
    * [`weights`](/input/option/weight)
        * **Description**: Please see section on the [weight](/input/option/weight)
option for more details.
        * **Type**: List[Weight]
        * **Required**: False
        * **Default**: `null`
    * [`regexes`](/input/option/regex)
        * **Description**: Please see section on the [regex](/input/option/regex)
option for more details.
        * **Type**: List[Regex]
        * **Required**: False
        * **Default**: `null`
* hierarchical options
    * [`whitelist`](/input/option/blackwhitelist)
    * [`blacklist`](/input/option/blackwhitelist)
    * [`regex`](/input/option/regex)
    * [`priority`](/input/option/priority)
    * [`weight`](/input/option/weight)
    * [`timed`](/input/option/timed)
