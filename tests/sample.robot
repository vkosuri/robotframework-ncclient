*** Settings ***
Library   NcclientLibrary

*** Test Cases ***
Test-Login
    ${config} =  Create Dictionary  host=10.11.13.22  port=830  username=root  password=password  hostkey_verify=False
    Connect  &{config}
    Close Session

