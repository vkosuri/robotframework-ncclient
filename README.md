
[![PyPi downloads](https://img.shields.io/pypi/dm/robotframework-ncclient.svg)](https://pypi.python.org/pypi/robotframework-ncclient)
[![Latest Version](https://img.shields.io/pypi/v/robotframework-ncclient.svg)](https://pypi.python.org/pypi/robotframework-ncclient)

# NcclientLibrary

NcclientLibrary is a [Robotframework](https://github.com/robotframework/robotframework) NETCONF wrapper libraray of [ncclient](https://github.com/ncclient/ncclient)

``` bash
pip install robotframework-ncclient
```

If you stuck with any errors please try to install all these packages.

```bash
sudo apt install libpq-dev python-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev
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
