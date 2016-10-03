
[![PyPi downloads](https://img.shields.io/pypi/dm/robotframework-ncclient.svg)](https://pypi.python.org/pypi/robotframework-ncclient)
[![Latest Version](https://img.shields.io/pypi/v/robotframework-ncclient.svg)](https://pypi.python.org/pypi/robotframework-ncclient)

# NcclientLibrary

NcclientLibrary is a [Robotframework](https://github.com/robotframework/robotframework) NETCONF wrapper libraray of [ncclient](https://github.com/ncclient/ncclient)

``` bash
pip install robotframework-ncclient
```

If you stuck with any errors please try to install all these packages.

```bash
sudo apt-get install build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3 python-dev
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
