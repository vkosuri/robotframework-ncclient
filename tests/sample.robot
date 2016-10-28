*** Settings ***
Suite Setup  Connect  alias=${ALIAS}  host=${HOST}  port=${PORT}  username=${USERNAME}  password=${PASSWORD}  hostkey_verify=False
Suite Teardown  Close Session  alias=${ALIAS}
Library  Collections
Library  NcclientLibrary
Library  String
Library  XML

*** Variables ***
${USERNAME}  root
${PASSWORD}  password
${HOST}  10.11.5.12
${PORT}  830
${ALIAS}  ncclient
*** Test Cases ***
Sample-Test-Pass
    [Tags]  Sample
    [Documentation]  *Retrieve all or part of a specified configuration datastore.*
    ...    https://tools.ietf.org/html/rfc6241#section-7.1
    ${xml}= <aaa xmlns="http://tail-f.com/ns/aaa/1.1"> <authentication><users><user><name/></user></users></authentication></aaa>
    ${res}=  Get  ${ALIAS}   ${xml}
