# NcclientLibrary

NcclientLibrary is a [Robotframework](https://github.com/robotframework/robotframework) NETCONF wrapper libraray of [ncclient](https://github.com/ncclient/ncclient)

``` bash
pip install robotframework-ncclient
```

## Example testcase

``` Robotframework
*** Settings ***
Library           NcclientLibrary

*** Test Cases ***
Test Login
    ${config} =    Create Dictionary    host=A.B.C.D    port=830    username=user    password=password    hostkey_verify=False
    Connect    &{config}
```

Pull requests are welcome.
