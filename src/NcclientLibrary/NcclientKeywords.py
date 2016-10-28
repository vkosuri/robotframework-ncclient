#!/usr/bin/env python

from ncclient import manager
from robot.api import logger
import re
import robot

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
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self._cache = robot.utils.ConnectionCache('No sessions created')

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
            alias = kwds.get('alias')
            session = manager.connect(
                host=kwds.get('host'),
                port=int(kwds.get('port') or 830),
                username=str(kwds.get('username')),
                password=str(kwds.get('password')),
                hostkey_verify=False,
                key_filename=str(kwds.get('key_filename')),
            )
            self._cache.register(session, alias=alias)
            all_server_capabilities = session.server_capabilities
            self.client_capabilities = session.client_capabilities
            self.session_id = session.session_id
            self.connected = session.connected
            self.timeout = session.timeout
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

    def get_config(self, alias, source, filter_type='subtree',
                    filter_criteria=None):
        """
        Retrieve all or part of a specified configuration.

        ``alias`` that will be used to identify the Session object in the cache

        ``source`` name of the configuration datastore being queried

        ``filter_type`` xml string or subtree value

        ``filter_criteria`` tuple values (xml and xpath)

        **Filter parameters**

        Where a method takes a filter argument, it can take on the following
        type:

        A tuple of (type, criteria).

            Here type has to be one of ``xpath`` or ``subtree``.
            For ``xpath`` the criteria should be a string containing the XPath
            expression.
            For ``subtree`` the criteria should be an XML string or an Element
            object containing the criteria.

        A <filter> element as an XML string or an Element object.
        """
        session = self._cache.switch(alias)
        gc_filter = None
        try:
            if filter_criteria:
                gc_filter = (filter_type, filter_criteria)

            logger.info("alias: %s, source: %s, filter: %s:" % (alias, source,
                                                                gc_filter))
            return session.get_config(source, gc_filter).data
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def edit_config(self, alias, target, config, default_operation=None,
                                    test_option=None, error_option=None):
        """
        Loads all or part of the specified config to the target
         configuration datastore.

        ``alias`` that will be used to identify the Session object in the cache

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
        session = self._cache.switch(alias)

        try:
            logger.info("target: %s, config: %s, default_operation: %s \
               test_option: %s,  error_option: %s" 
               % (target, config, default_operation, test_option, error_option))
            session.edit_config(target, config, default_operation, 
                                    test_option, error_option)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def copy_config(self, alias, source, target):
        """
        Create or replace an entire configuration datastore with the contents
        of another complete configuration datastore.

        ``alias`` that will be used to identify the Session object in the cache

        ``source`` is the name of the configuration datastore to use as the
        source of the copy operation or config element containing the
        configuration subtree to copy

        ``target`` is the name of the configuration datastore to use as the
        destination of the copy operation
        """
        session = self._cache.switch(alias)
        try:
            logger.info("alias: %s, source: %s, target: %s" % (alias, source,
                                                                target))
            session.copy_config(source, target)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def delete_config(self, alias, target):
        """
        Delete a configuration datastore.

        ``alias`` that will be used to identify the Session object in the cache

        ``target`` specifies the name or URL of configuration datastore to
        delete.
        """
        session = self._cache.switch(alias)
        try:
            logger.info("alias: %s, target: %s" % (alias, target))
            session.delete_config(target)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def dispatch(self, alias, rpc_command, source=None, filter=None):
        """
        ``alias`` that will be used to identify the Session object in the cache

        ``rpc_command`` specifies rpc command to be dispatched either in plain
        text or in xml element format (depending on command)

        ``source`` name of the configuration datastore being queried

        ``filter`` specifies the portion of the configuration to retrieve
        (by default entire configuration is retrieved)
        """
        session = self._cache.switch(alias)
        try:
            logger.info("alias: %s, rpc_command: %s, source: %s, filter: %s" 
                                    % (alias, rpc_command, source, filter))
            session.dispatch(rpc_command, source, filter)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def lock(self, alias, target):
        """
        Allows the client to lock the configuration system of a device.

        ``alias`` that will be used to identify the Session object in the cache

        ``target`` is the name of the configuration datastore to lock
        """
        session = self._cache.switch(alias)
        try:
            logger.info("alias: %s, target: %s" % (alias, target))
            session.lock(target)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def unlock(self, alias, target):
        """
        Release a configuration lock, previously obtained with the lock
        operation.

        ``alias`` that will be used to identify the Session object in the cache

        ``target`` is the name of the configuration datastore to unlock
        """
        session = self._cache.switch(alias)
        try:
            logger.info("alias: %s, target: %s" % (alias, target))
            session.unlock(target)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def locked(self, alias, target):
        """
        Returns a context manager for a lock on a datastore, where target
        is the name of the configuration datastore to lock.

        ``alias`` that will be used to identify the Session object in the cache

        ``target`` is the name of the configuration datastore to unlock
        """
        session = self._cache.switch(alias)
        try:
            logger.info("alias: %s, target: %s" %(alias, target))
            session.locked(target)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def get(self, alias, filter_type='subtree', filter_criteria=None):
        """
        Retrieve running configuration and device state information.

        ``alias`` that will be used to identify the Session object in the cache

        ``filter_typoe`` specifies the portion of the configuration to retrieve (by
        default entire configuration is retrieved)

        ``filter_criteria`` A tuple of (xml, xpath)

        **Filter parameters**

        Where a method takes a filter argument, it can take on the following
        types:

        A tuple of (type, criteria).

            Here type has to be one of ``xpath`` or ``subtree``.
            For ``xpath`` the criteria should be a string containing the XPath
            expression.
            For ``subtree`` the criteria should be an XML string or an Element
            object containing the criteria.

        A <filter> element as an XML string or an Element object.
        """
        session = self._cache.switch(alias)
        get_filter = None
        try:
            if filter_criteria:
                get_filter = (filter_type, filter_criteria)
            return session.get(get_filter).data
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def close_session(self, alias):
        """
        Request graceful termination of the NETCONF session, and also close the
        transport.

        ``alias`` that will be used to identify the Session object in the cache
        """
        session = self._cache.switch(alias)
        try:
            session.close_session()
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def kill_session(self, alias, session_id):
        """
        Force the termination of a NETCONF session (not the current one!)

        ``alias`` that will be used to identify the Session object in the cache

        ``session_id`` is the session identifier of the NETCONF session to be
        terminated as a string
        """
        session = self._cache.switch(alias)
        try:
            logger.info("alias: %s, session_id: %s" %(alias, session_id))
            session.kill_session(session_id)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def commit(self, alias, confirmed=False, timeout=None):
        """
        Commit the candidate configuration as the device?s new current
        configuration. Depends on the :candidate capability.

        A confirmed commit (i.e. if confirmed is True) is reverted if there is
        no followup commit within the timeout interval. If no timeout is
        specified the confirm timeout defaults to 600 seconds (10 minutes). A
        confirming commit may have the confirmed parameter but this is not
        required. Depends on the :confirmed-commit capability.

        ``alias`` that will be used to identify the Session object in the cache

        ``confirmed`` whether this is a confirmed commit

        ``timeout`` specifies the confirm timeout in seconds
        """
        session = self._cache.switch(alias)
        try:
            logger.info("alias: %s, confirmed: %s, timeout:%s" % (alias,
                                                            confirmed, timeout))
            session.commit(confirmed, timeout)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def discard_changes(self, alias):
        """
        Revert the candidate configuration to the currently running
        configuration. Any uncommitted changes are discarded.

        ``alias`` that will be used to identify the Session object in the cache

        """
        session = self._cache.switch(alias)
        try:
            session.discard_changes()
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def validate(self, alias, source):
        """
        Validate the contents of the specified configuration.

        ``alias`` that will be used to identify the Session object in the cache

        ``source`` is the name of the configuration datastore being validated or
        config element containing the configuration subtree to be validated
        """
        session = self._cache.switch(alias)
        try:
            logger.info("alias: %s, source: %s" % (alias, source))
            session.validate(source)
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

    def close_session(self, alias):
        """
        Request graceful termination of the NETCONF session, and also close the
        transport.

        ``alias`` that will be used to identify the Session object in the cache
        """
        session = self._cache.switch(alias)
        try:
            session.close_session()
        except NcclientException as e:
            logger.error(str(e))
            raise str(e)

