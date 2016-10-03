#!/usr/bin/env python

from ncclient import manager
from robot.libraries.BuiltIn import BuiltIn
import collections


def _convert_keys_to_string(data):
    """ Convert unicode dict values into strings
    because robotframwork uses unicode values
    """
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(_convert_keys_to_string, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(_convert_keys_to_string, data))
    else:
        return data


class NcclientException(Exception):
    pass


class NcclientKeywords(object):
    def __init__(self):
        self.builtin = BuiltIn()
        self.m = None
        # Specify whether operations are executed asynchronously (True) or 
        # synchronously (False) (the default).
        self.async_mode = None
        # Specify the timeout for synchronous RPC requests.
        self.timeout = None
        # Specify which errors are raised as RPCError exceptions. Valid values are 
        # the constants defined in RaiseMode. The default value is ALL.
        self.raise_mode = None       
        # Capabilities object representing the client?s capabilities.
        self.client_capabilities = None
        # Capabilities object representing the server?s capabilities.
        self.server_capabilities = None
        # session-id assigned by the NETCONF server.
        self.session_id = None
        # Whether currently connected to the NETCONF server.
        self.connected = None

    def connect(self, *args, **kwds):
        """
        Initialize a Manager over the SSH transport.
        """        
        try:
            self.builtin.log('Creating session %s, %s' % (args, kwds))            
            self.m = manager.connect(args, _convert_keys_to_string(kwds))
            # self.async_mode = self.m.async_mode
            # self.timeout = self.m.timeout
            # self.raise_mode = self.m.raise_mode                  
            # self.client_capabilities = self.m.client_capabilities
            # self.server_capabilities = self.m.server_capabilities
            # self.session_id = self.m.session_id
            # self.connected = self.m.connected
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)    

    def get_config(self, source, filter=None):
        """
        Retrieve all or part of a specified configuration.

        ``source`` name of the configuration datastore being queried

        ``filter`` specifies the portion of the configuration to retrieve 
        (by default entire configuration is retrieved)
        """        
        try:
            self.builtin.log("source: %s, filter: %s:" % (source, filter))
            self.m.get_config(source, filter)
        except NcclientException as e:
            print str(e)
            self.builtin.log(str(e))
            raise str(e)

    def edit_config(self, target, config, default_operation=None, test_option=None, error_option=None):
        """
        Loads all or part of the specified config to the target configuration datastore.

        ``target`` is the name of the configuration datastore being edited

        ``config`` is the configuration, which must be rooted in the config element. 
        It can be specified either as a string or an Element.

        ``default_operation`` if specified must be one of { ?merge?, ?replace?, or ?none? }

        ``test_option`` if specified must be one of { ?test_then_set?, ?set? }

        ``error_option`` if specified must be one of 
        { ?stop-on-error?, ?continue-on-error?, ?rollback-on-error? }

        The ?rollback-on-error? error_option depends on the :rollback-on-error capability.

        """        
        try:
            self.builtin.log("target: %s, config: %s, default_operation: %s \
               test_option: %s,  error_option: %s" % (target, config, default_operation, test_option, error_option))
            self.m.edit_config(target, config, default_operation, test_option, error_option)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)
    
    def copy_config(self, source, target):
        """
        Create or replace an entire configuration datastore with the contents 
        of another complete configuration datastore.

        ``source`` is the name of the configuration datastore to use as the 
        source of the copy operation or config element containing the configuration subtree to copy

        ``target`` is the name of the configuration datastore to use as the 
        destination of the copy operation
        """        
        try:
            self.builtin.log("source: %s, target: %s" % (source, target))
            self.m.copy_config(source, target)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)
        
    def delete_config(self, target):
        """
        Delete a configuration datastore.

        ``target`` specifies the name or URL of configuration datastore to delete
        """        
        try:
            self.builtin.log("target: %s" % target)
            self.m.delete_config(target)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)
        
    def dispatch(self, rpc_command, source=None, filter=None):
        """
        ``rpc_command`` specifies rpc command to be dispatched either in plain 
        text or in xml element format (depending on command)

        ``source`` name of the configuration datastore being queried

        ``filter`` specifies the portion of the configuration to retrieve 
        (by default entire configuration is retrieved)
        """        
        try:
            self.builtin.log("rpc_command: %s, source: %s, filter: %s" % (rpc_command, source, filter))
            self.m.dispatch(rpc_command, source, filter)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)
        
    def lock(self, target):
        """
        Allows the client to lock the configuration system of a device.

        ``target`` is the name of the configuration datastore to lock
        """
        try:
            self.builtin.log("target: %s" % target)
            self.m.lock(target)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)

    def unlock(self, target):
        """
        Release a configuration lock, previously obtained with the lock operation.

        ``target`` is the name of the configuration datastore to unlock
        """
        try:
            self.builtin.log("target: %s" % target)
            self.m.unlock(target)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)
        
    def locked(self, target):
        """
        Returns a context manager for a lock on a datastore, where target 
        is the name of the configuration datastore to lock.
        """
        try:
            self.builtin.log("target: %s" % target)
            self.m.locked(target)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)
    
    def get(self):
        """
        Retrieve running configuration and device state information.

        filter specifies the portion of the configuration to retrieve (by default entire configuration is retrieved)
        """
        try:
            self.m.get()
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)

    def close_session(self):
        """
        Request graceful termination of the NETCONF session, and also close the transport.
        """
        try:
            self.m.close_session()
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)

    def kill_session(self, session_id):
        """
        Force the termination of a NETCONF session (not the current one!)

        ``session_id`` is the session identifier of the NETCONF session to be terminated as a string
        """
        try:
            self.builtin.log("session_id: %s" % session_id)
            self.m.kill_session(session_id)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)
    
    def commit(self, confirmed=False, timeout=None):
        """
        Commit the candidate configuration as the device?s new current configuration.
        Depends on the :candidate capability.

        A confirmed commit (i.e. if confirmed is True) is reverted if there is no
        followup commit within the timeout interval. If no timeout is specified the confirm
        timeout defaults to 600 seconds (10 minutes). A confirming commit may have the
        confirmed parameter but this is not required. Depends on the :confirmed-commit capability.

        ``confirmed`` whether this is a confirmed commit

        ``timeout`` specifies the confirm timeout in seconds
        """
        try:
            self.builtin.log("confirmed: %s, timeout:%s" % (confirmed, timeout))
            self.m.commit(confirmed, timeout)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)
    
    def discard_changes(self):
        """
        Revert the candidate configuration to the currently running configuration.
        Any uncommitted changes are discarded.
        """
        try:
            self.m.discard_changes()
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)

    def validate(self, source):
        """
        Validate the contents of the specified configuration.

        ``source`` is the name of the configuration datastore being validated or config
        element containing the configuration subtree to be validated
        """
        try:
            self.builtin.log("source: %s" % source)
            self.m.validate(source)
        except NcclientException as e:
            self.builtin.log(str(e))
            print str(e)
            raise str(e)
