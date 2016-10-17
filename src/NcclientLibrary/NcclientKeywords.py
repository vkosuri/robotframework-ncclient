#!/usr/bin/env python

from ncclient import manager
from robot.api import logger
import re

_standard_capabilities = {
    # The server supports the <candidate/> database
    "candidate" : False,
    # :candidate capability support
    "confirmed-commit" : False,
    # The server will accepts <rpc> requests"
    "interleave" :  False,
    # basic notification delivery support
    "notification": False,
    # supports the <partial-lock> and <partial-unlock>
    "partial-lock" : False,
    # 'roolback-on-error' value for the <error-option> and <edit-config>
    # operations
    "roolback-on-error" : False,
    # <startup/> database support
    "starup" : False,
    # Indicates file, https and stftp server capabilities
    "url" : False,
    # <validate> operation
    "validate" : False,
    # allow the client to change the running configuration directly
    "writable-running" : False,
    # The server fully supports the XPATH 1.0 sepcification for fliter data
    "xpath" : False
}

class NcclientException(Exception):
    pass


class NcclientKeywords(object):
    def __init__(self):
        # manager object
        self.mgr = None
        # Specify whether operations are executed asynchronously (True) or 
        # synchronously (False) (the default).
        self.async_mode = None
        # Specify the timeout for synchronous RPC requests.
        self.timeout = None
        # Specify which errors are raised as RPCError exceptions. Valid values
        # are the constants defined in RaiseMode. The default value is ALL.
        self.raise_mode = None
        # Capabilities object representing the client's capabilities.
        self.client_capabilities = None
        # Capabilities object representing the server's capabilities.
        self.server_capabilities = _standard_capabilities
        # YANG modules supported by server
        self.yang_modules = None
        # session-id assigned by the NETCONF server.
        self.session_id = None
        # Whether currently connected to the NETCONF server.
        self.connected = None

    def connect(self, *args, **kwds):
        """
        Initialize a Manager over the SSH transport.
        """
        try:
            logger.info('Creating session %s, %s' % (args, kwds))
            self.mgr = manager.connect(
                host=kwds.get('host'),
                port=int(kwds.get('port') or 830),
                username=str(kwds.get('username')),
                password=str(kwds.get('password')),
                hostkey_verify=False,
                key_filename=str(kwds.get('key_filename')),
            )
            all_server_capabilities = self.mgr.server_capabilities
            self.client_capabilities = self.mgr.client_capabilities
            self.session_id = self.mgr.session_id
            self.connected = self.mgr.connected
            self.timeout = self.mgr.timeout
            # Store YANG Modules and Capabilities
            self.yang_modules, server_capabilities = \
                    self._parse_server_capabilities(all_server_capabilities)
            # Parse server capabilities
            for sc in server_capabilities:
                self.server_capabilities[sc] = True

            logger.debug("%s, %s, %s, %s" %(self.server_capabilities, 
                        self.yang_modules, self.client_capabilities,
                        self.timeout))
            return True
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def get_server_capabilities(self):
        """ Returns server caps """
        return self.server_capabilities

    def get_yang_modules(self):
        """ Returns server supported YANG modules """
        return self.yang_modules

    def _parse_server_capabilities(self, server_capabilities):
        """
        Returns server_capabilities and supported YANG modules in JSON format
        """
        module_list = []
        server_caps = []
        try:
            for sc in server_capabilities:
                # urn:ietf:params:netconf:capability:{name}:1.x
                server_caps_match = re.match(
                        r'urn:ietf:params:netconf:capability:(\S+):\d+.\d+',
                        sc)
                if server_caps_match:
                    server_caps.append(server_caps_match.group(1))
                modules_match = re.findall(
                    r'(\S+)\?module=(\S+)&revision=' +
                    '(\d{4}-\d{2}-\d{2})&?(features=(\S+))?',
                    sc)
                if modules_match:
                    namespace, name, revision, _, features = modules_match[0]
                    if features:
                        module_list.append(
                            {"name": name, "revision": revision,
                            "namespace": namespace,
                            "features": features.split(",")})
                    else:
                        module_list.append({"name":name,
                                            "revision":revision,
                                            "namespace": namespace})

            module_dict = {"module-info": module_list}
            return module_dict, server_caps
        except NcclientException as e:
            logger.error(list(server_capabilities))
            logger.error(str(e))
            raise str(e)

    def get_config(self, source, filter=None):
        """
        Retrieve all or part of a specified configuration.

        ``source`` name of the configuration datastore being queried

        ``filter`` specifies the portion of the configuration to retrieve
        (by default entire configuration is retrieved)
        """
        try:
            logger.info("source: %s, filter: %s:" % (source, filter))
            self.mgr.get_config(source, filter)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def edit_config(self, target, config, default_operation=None,
                                    test_option=None, error_option=None):
        """
        Loads all or part of the specified config to the target
         configuration datastore.

        ``target`` is the name of the configuration datastore being edited

        ``config`` is the configuration, which must be rooted in the config
        element.  It can be specified either as a string or an Element.

        ``default_operation`` if specified must be one of 
        { ?merge?, ?replace?, or ?none? }

        ``test_option`` if specified must be one of { ?test_then_set?, ?set? }

        ``error_option`` if specified must be one of
        { ?stop-on-error?, ?continue-on-error?, ?rollback-on-error? }

        The ?rollback-on-error? error_option depends on the :rollback-on-error
        adaptability.

        """
        try:
            logger.info("target: %s, config: %s, default_operation: %s \
               test_option: %s,  error_option: %s" 
               % (target, config, default_operation, test_option, error_option))
            self.mgr.edit_config(target, config, default_operation, 
                                    test_option, error_option)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def copy_config(self, source, target):
        """
        Create or replace an entire configuration datastore with the contents
        of another complete configuration datastore.

        ``source`` is the name of the configuration datastore to use as the
        source of the copy operation or config element containing the
        configuration subtree to copy

        ``target`` is the name of the configuration datastore to use as the
        destination of the copy operation
        """
        try:
            logger.info("source: %s, target: %s" % (source, target))
            self.mgr.copy_config(source, target)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def delete_config(self, target):
        """
        Delete a configuration datastore.

        ``target`` specifies the name or URL of configuration datastore to
        delete.
        """
        try:
            logger.info("target: %s" % target)
            self.mgr.delete_config(target)
        except NcclientException as e:
            logger.error(str(e))
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
            logger.info("rpc_command: %s, source: %s, filter: %s" 
                                    % (rpc_command, source, filter))
            self.mgr.dispatch(rpc_command, source, filter)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def lock(self, target):
        """
        Allows the client to lock the configuration system of a device.

        ``target`` is the name of the configuration datastore to lock
        """
        try:
            logger.info("target: %s" % target)
            self.mgr.lock(target)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def unlock(self, target):
        """
        Release a configuration lock, previously obtained with the lock
        operation.

        ``target`` is the name of the configuration datastore to unlock
        """
        try:
            logger.info("target: %s" % target)
            self.mgr.unlock(target)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def locked(self, target):
        """
        Returns a context manager for a lock on a datastore, where target
        is the name of the configuration datastore to lock.
        """
        try:
            logger.info("target: %s" % target)
            self.mgr.locked(target)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def get(self):
        """
        Retrieve running configuration and device state information.

        filter specifies the portion of the configuration to retrieve (by
        default entire configuration is retrieved)
        """
        try:
            self.mgr.get()
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def close_session(self):
        """
        Request graceful termination of the NETCONF session, and also close the
        transport.
        """
        try:
            self.mgr.close_session()
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def kill_session(self, session_id):
        """
        Force the termination of a NETCONF session (not the current one!)

        ``session_id`` is the session identifier of the NETCONF session to be
        terminated as a string
        """
        try:
            logger.info("session_id: %s" % session_id)
            self.mgr.kill_session(session_id)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def commit(self, confirmed=False, timeout=None):
        """
        Commit the candidate configuration as the device?s new current
        configuration. Depends on the :candidate capability.

        A confirmed commit (i.e. if confirmed is True) is reverted if there is
        no followup commit within the timeout interval. If no timeout is
        specified the confirm timeout defaults to 600 seconds (10 minutes). A
        confirming commit may have the confirmed parameter but this is not
        required. Depends on the :confirmed-commit capability.

        ``confirmed`` whether this is a confirmed commit

        ``timeout`` specifies the confirm timeout in seconds
        """
        try:
            logger.info("confirmed: %s, timeout:%s" % (confirmed, timeout))
            self.mgr.commit(confirmed, timeout)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def discard_changes(self):
        """
        Revert the candidate configuration to the currently running
        configuration. Any uncommitted changes are discarded.
        """
        try:
            self.mgr.discard_changes()
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def validate(self, source):
        """
        Validate the contents of the specified configuration.

        ``source`` is the name of the configuration datastore being validated or
        config element containing the configuration subtree to be validated
        """
        try:
            logger.info("source: %s" % source)
            self.mgr.validate(source)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def close_session(self):
        """
        Request graceful termination of the NETCONF session, and also close the
        transport.
        """
        try:
            self.mgr.close_session()
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

