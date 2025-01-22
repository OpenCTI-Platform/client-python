import secrets

from typing import List, Dict


class User:
    """Representation of a user on the OpenCTI platform

    Users can be member of multiple groups, from which its permissions
    (capabilities) are derived. Additionally, users are part of organisations,
    and sometimes administrating them (Enterprise edition).

    They have configured confidence, and an effective confidence (which might
    be set by the group).

    Representation of a User::

        {
            "id": "UUID",
            "individual_id": "UUID of Creator object for user",
            "user_email": "Email address assigned to user",
            "firstname": "First name",
            "lastname": "Last name",
            "name": "Name",
            "description": "This is a user",
            "language": "auto",
            "theme": "light|dark|auto",
            "unit_system": "auto|Metric|Imperial",
            "external": true,
            "restrict_delete": true,
            "account_status": "active",
            "account_lock_after_date": "ISO 8601 date",
            "created_at": "ISO 8601 date",
            "updated_at": "ISO 8601 date",
            "roles": [{
                "id": "UUID",
                "name": "Role name",
                "description": "Role description",
                "capabilities": [{
                    "id": "UUID",
                    "name": "KNUPDATE"
                }]
            }],
            "capabilities": [{
                "id": "UUID",
                "name": "KNUPDATE"
            }],
            "groups": {
                "edges": [{
                    "node": {
                        "id": "UUID",
                        "name": "group name",
                        "description": "Group description"
                    }
                }]
            },
            "objectOrganization": {
                "edges": [{
                    "node": {
                        "id": "UUID",
                        "is_inferred": false,
                        "name": "Org name",
                        "description": "Organisation description"
                    }
                }]
            },
            "administrated_organizations": [{
                "id": "UUID",
                "name": "Org name",
                "description": "Organisation description"
            }],
            "user_confidence_level": {
                "max_confidence": 90,
                "overrides": [{
                    "entity_type": "type",
                    "max_confidence": 100
                }]
            },
            "effective_confidence_level": {
                "max_confidence": 90,
                "source": {
                    "type": "User|Group|Bypass",
                    "object": { # Only on type == Group
                        "id": "UUID",
                        "name": "group name"
                    }
                },
                "overrides": {
                    "entity_type": "type",
                    "max_confidence": 90,
                    "source": {
                        "type": "User|Group|Bypass",
                        "object": { # Only on type == Group
                            "id": "UUID",
                            "name": "group name"
                        }
                    }
                }
            },
            "api_token": "API_KEY", # only available if requested
            "sessions": [{
                "id": "UUID",
                "created": "ISO 8901 datetime",
                "ttl": 100,
                "originalMaxAge": 100
            }], # only available if requested
            "submenu_show_icons": true, # only for MeUser
            "submenu_auto_collaps": true # only for MeUser
        }

    You can view the properties, token_properties, session_properties, and
    me_properties attributes of a User object to view what attributes will be
    present in a User or MeUser object.
    """

    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            standard_id
            individual_id
            user_email
            firstname
            lastname
            name
            description

            language
            theme
            unit_system

            external
            restrict_delete

            account_status
            account_lock_after_date

            created_at
            updated_at

            unit_system
            submenu_show_icons
            submenu_auto_collapse
            monochrome_labels

            roles {
                id, name, description
                capabilities {
                    id, name
                }
            }

            groups {
                edges {
                    node {
                        id, name, description
                    }
                }
            }

            objectOrganization {
                edges {
                    node {
                        id, is_inferred, name, description
                    }
                }
            }

            administrated_organizations {
                id, name, description
            }

            user_confidence_level {
                max_confidence
                overrides {
                    entity_type, max_confidence
                }
            }
            effective_confidence_level {
                max_confidence
                source {
                    type
                    object {
                        ... on Group {
                            id, name
                        }
                    }
                }
                overrides {
                    entity_type, max_confidence
                    source {
                        type
                        object {
                            ... on Group {
                                id, name
                            }
                        }
                    }
                }
            }
        """

        self.token_properties = """
            api_token
        """

        self.session_properties = """
            sessions {
                id, created, ttl, originalMaxAge
            }
        """

        self.me_properties = """
            id
            individual_id
            user_email
            firstname
            lastname
            name
            description

            theme
            language
            unit_system
            submenu_show_icons
            submenu_auto_collapse

            objectOrganization {
                edges {
                    node {
                        id, name
                    }
                }
            }

            administrated_organizations {
                id, name
            }

            capabilities {
                id, name, description
            }

            groups {
                edges {
                    node {
                        id, name, description
                    }
                }
            }

            effective_confidence_level {
                max_confidence
                source {
                    type
                    object {
                        ... on Group {
                            id, name
                        }
                    }
                }
                overrides {
                    entity_type, max_confidence
                    source {
                        type
                        object {
                            ... on Group {
                                id, name
                            }
                        }
                    }
                }
            }
        """

    def list(self,
             first: int = 500,
             after: str = None,
             orderBy: str = "name",
             orderMode: str = "asc",
             filters: dict = {},
             search: str = None,
             include_sessions: bool = False,
             customAttributes: str = None,
             getAll: bool = False,
             withPagination: bool = False) -> List[Dict]:
        """Search/list users on the platform

        Searches users given some conditions. Defaults to listing all users.

        :param first: Defaults to 500. Retrieve this number of results.
        :type first: int, optional
        :param after: Retrieves all results after the user with this ID.
            Ignored if None, empty, or if fetching all results, defaults to
            None.
        :type after: str, optional
        :param orderBy:  Orders results by this field.
            Can be one of user, user_email, firstname, lastname, language,
            external, created_at, updated_at, or _score, defaults to "name".
        :type orderBy: str, optional
        :param orderMode:  Ordering direction. Must be one
            of "asc" or "desc", defaults to "asc".
        :type orderMode: str, optional
        :param filters:  OpenCTI API FilterGroup object.
            This is an advanced parameter. To learn more please search for
            the FilterGroup object in the OpenCTI GraphQL Playground, defaults
            to {}.
        :type filters: dict, optional
        :param search:  String to search for when listing
            users, defaults to None.
        :type search: str, optional
        :param include_sessions:  Whether or not to
            include a list of sessions with results, defaults to False.
        :type include_sessions: bool, optional
        :param customAttributes: Custom attributes to fetch from the GraphQL
            query
        :type customAttributes: str, optional
        :param getAll: Defaults to False. Whether or not to get all results
            from the search. If True then param first is ignored.
        :type getAll: bool, optional
        :param withPagination: Defaults to False. Whether to return pagination
            info with results.
        :type withPagination: bool, optional
        :return: Returns a list of users, sorted as specified.
        :rtype: list[dict]
        """
        if getAll:
            first = 100

        self.opencti.admin_logger.info("Fetching users with filters",
                                       {"filters": filters})
        query = (
            """
            query ListUsers($first: Int, $after: ID, $orderBy: UsersOrdering, $orderMode: OrderingMode, $filters: FilterGroup, $search: String) {
                users(first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode, filters: $filters, search: $search) {
                    edges {
                        node {
                    """
            + (self.properties if customAttributes is None
               else customAttributes)
            + (self.session_properties if include_sessions else "")
            + """
                        }
                    }

                    pageInfo {
                        startCursor, endCursor, hasNextPage, hasPreviousPage
                        globalCount
                    }
                }
            }
            """
        )
        result = self.opencti.query(query, {
            "first": first,
            "after": after,
            "orderBy": orderBy,
            "orderMode": orderMode,
            "filters": filters,
            "search": search
        })

        if getAll:
            final_data = []
            data = self.opencti.process_multiple(result["data"]["users"])
            final_data = final_data + data
            while result["data"]["users"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["users"]["pageInfo"]["endCursor"]
                result = self.opencti.query(query, {
                    "first": first,
                    "after": after,
                    "orderBy": orderBy,
                    "orderMode": orderMode,
                    "filters": filters,
                    "search": search
                })
                data = self.opencti.process_multiple(result["data"]["users"])
                final_data = final_data + data
            return final_data
        else:
            return self.opencti.process_multiple(result["data"]["users"],
                                                 withPagination)

    def read(self,
             id: str = None,
             include_sessions: bool = False,
             include_token: bool = False,
             customAttributes: str = None,
             filters: dict = None,
             search: str = None) -> dict:
        """Reads user details from the platform.

        :param id: ID of the user to fetch
        :type id: str, optional
        :param include_sessions:  Whether or not to
            include a list of sessions for the given user, defaults to False.
        :type include_sessions: bool, optional
        :param include_token:  Whether or not to include
            the user's API token, defaults to False.
        :type include_token: bool, optional
        :param customAttributes: Custom attributes to include instead of the
            defaults
        :type customAttribues: str, optional
        :param filters: Filters to apply to find a single user
        :type filters: dict, optional
        :param search: Search term to use to find a single user
        :type search: str, optional
        :return: Representation of the user as a Python dictionary.
        :rtype: dict
        """
        if id is not None:
            self.opencti.admin_logger.info(
                "Fetching user with ID", {"id": id}
            )
            query = (
                """
                query User($id: String!) {
                    user(id: $id) {
                        """
                + (self.properties if customAttributes is None
                   else customAttributes)
                + (self.token_properties if include_token else "")
                + (self.session_properties if include_sessions else "")
                + """
                    }
                }
                """
            )
            result = self.opencti.query(query, {"id": id})
            return self.opencti.process_multiple_fields(result["data"]["user"])
        elif filters is not None or search is not None:
            results = self.list(
                filters=filters,
                search=search,
                include_sessions=include_sessions,
                customAttributes=customAttributes)
            user = results[0] if results else None
            if not include_token or user is None:
                return user
            else:
                return self.read(
                    id=user["id"],
                    include_sessions=include_sessions,
                    include_token=include_token,
                    customAttributes=customAttributes
                )
        else:
            self.opencti.admin_logger.error(
                "[opencti_user] Missing paramters: id, search, or filters")
            return None

    def create(self,
               name: str,
               user_email: str,
               password: str = None,
               firstname: str = None,
               lastname: str = None,
               description: str = None,
               language: str = None,
               theme: str = None,
               objectOrganization: List[str] = None,
               account_status: str = None,
               account_lock_after_date: str = None,
               unit_system: str = None,
               submenu_show_icons: bool = False,
               submenu_auto_collapse: bool = False,
               monochrome_labels: bool = False,
               groups: List[str] = None,
               user_confidence_level: Dict = None,
               customAttributes: str = None,
               include_token: bool = False) -> dict:
        """Creates a new user with basic details

        Note that when SSO is connected users generally do not need to be
        manually created.

        Additionally note that if there is no password passed to this function
        then a random password will be created and will not be returned. This
        is useful for creating service accounts and connector accounts.

        :param name: Name to assign to the user.
        :type name: str
        :param user_email: Email address for the user.
        :type user_email: str
        :param password:  Password that should be assigned
            to the user. If one is not provided then a random one will be
            generated, defaults to None.
        :type password: str, optional
        :param firstname: First name of the user
        :type firstname: str, optional
        :param lastname: Last name of the user
        :type lastname: str, optional
        :param description: Description for the user
        :type description: str, optional
        :param language: Language the user should use
        :type language: str, optional
        :param theme: Theme to set for the user, either light or dark
        :type theme: str, optional
        :param objectOrganization: List of organization IDs to add the user to
        :type objectOgranization: List[str], optional
        :param account_status: The status of the account: Active, Expired,
            Inactive, or Locked
        :type account_status: str, optional
        :param account_lock_after_date: ISO 8901 of when account should be
            locked
        :type account_lock_after_date: str, optional
        :param unit_system: Unit system for the user, metric or imperial
        :type unit_system: str, optional
        :param submenu_show_icons: Defaults to False. Whether or not to show
            icons in submenus on the left hand menu bar in the UI
        :type submenu_show_icons: bool, optional
        :param submenu_auto_collaps: Defaults to False. Whether to auto-
            collapse the left hand menu bar in the UI
        :type submenu_auto_collapse: bool, optional
        :param monochrome_labels: Defaults to False. Whether to ignore colours
            and just show entity labels in monochrome.
        :type monochrome_labels: bool, optional
        :param groups: List of group IDs to add the user to
        :type groups: List[str], optional
        :param user_confidence_level: Confidence level object to assign to the
            user. This may not impact effective confidence depending on group
            membership.
        :type user_confidence_level: Dict
        :param customAttributes: Custom attributes to return for the user
        :type customAttributes: str, optional
        :param include_token: Defaults to False. Whether to include the API
            token for the new user in the response.
        :type include_token: bool, optional
        :return: Representation of the user without sessions or API token.
        :rtype: dict
        """
        self.opencti.admin_logger.info(
            "Creating a new user", {"name": name, "email": user_email})
        if password is None:
            self.opencti.admin_logger.info(
                "Generating random password for user", {
                    "name": name, "user_email": user_email
                })
            password = secrets.token_urlsafe(64)
        query = (
            """
            mutation UserAdd($input: UserAddInput!) {
                userAdd(input: $input) {
                    """
            + (self.properties if customAttributes is None
               else customAttributes)
            + (self.token_properties if include_token else "")
            + """
                }
            }
            """
        )
        result = self.opencti.query(query, {"input": {
            "user_email": user_email,
            "name": name,
            "password": password,
            "firstname": firstname,
            "lastname": lastname,
            "description": description,
            "language": language,
            "theme": theme,
            "objectOrganization": objectOrganization,
            "account_status": account_status,
            "account_lock_after_date": account_lock_after_date,
            "unit_system": unit_system,
            "submenu_show_icons": submenu_show_icons,
            "submenu_auto_collapse": submenu_auto_collapse,
            "monochrome_labels": monochrome_labels,
            "groups": groups,
            "user_confidence_level": user_confidence_level
        }})
        return self.opencti.process_multiple_fields(
            result["data"]["userAdd"])

    def delete(self, id: str):
        """Deletes the given user from the platform.

        :param id: ID of the user to delete.
        :type id: str
        """
        self.opencti.admin_logger.info("Deleting user", {"id": id})
        query = """
            mutation DeleteUser($id: ID!) {
                userEdit(id: $id) {
                    delete
                }
            }
        """
        self.opencti.query(query, {"id": id})

    def me(self,
           include_token: bool = False,
           customAttributes: str = None) -> dict:
        """Reads the currently authenticated user.

        :param include_token:  Whether to inclued the API
            token of the currently authenticated user, defaults to False.
        :type include_token: bool, optional
        :param customAttributes: Custom attributes to return on the User
        :type customAttributes: str, optional
        :return: Representation of the user.
        :rtype: dict
        """
        self.opencti.admin_logger.info("Reading MeUser")
        query = (
            """
            query Me {
                me {
                    """
            + (self.me_properties if customAttributes is None
               else customAttributes)
            + (self.token_properties if include_token else "")
            + """
                }
            }
            """
        )
        result = self.opencti.query(query)
        return self.opencti.process_multiple_fields(result["data"]["me"])

    def update_field(self,
                     id: str,
                     input: List[Dict],
                     customAttributes: str = None) -> Dict:
        """Update a given user using fieldPatch

        :param id: ID of the user to update.
        :type id: str
        :param input: FieldPatchInput objects to edit user
        :type input: List[Dict]
        :param customAttributes: Custom attributes to return from the mutation
        :type customAttributes: str, optional
        :return: Representation of the user without sessions or API token.
        :rtype: dict
        """
        self.opencti.admin_logger.info(
            "Editing user with input (not shown to hide password and API token"
            " changes)", {"id": id})
        query = (
            """
            mutation UserEdit($id: ID!, $input: [EditInput]!) {
                userEdit(id: $id) {
                    fieldPatch(input: $input) {
                        """
            + (self.properties if customAttributes is None
               else customAttributes)
            + """
                    }
                }
            }
            """
        )
        result = self.opencti.query(query, {"id": id, "input": input})
        return self.opencti.process_multiple_fields(
            result["data"]["userEdit"]["fieldPatch"])

    def add_membership(self,
                       id: str,
                       group_id: str) -> dict:
        """Adds the user to a given group.

        :param id: User ID to add to the group.
        :type id: str
        :param group_id: Group ID to add the user to.
        :type group_id: str
        :return: Representation of the InternalRelationship
        :rtype: dict
        """
        self.opencti.admin_logger.info("Adding user to group", {
            "id": id, "group_id": group_id
        })
        query = """
            mutation UserAddMembership($id: ID!, $group_id: ID!) {
                userEdit(id: $id) {
                    relationAdd(input: {
                        relationship_type: "member-of",
                        toId: $group_id
                    }) {
                        id
                        from {
                            ... on User {
                                id, name, user_email
                            }
                        }
                        to {
                            ... on Group {
                                id, name, description
                            }
                        }
                    }
                }
            }
        """
        result = self.opencti.query(query, {"id": id, "group_id": group_id})
        return self.opencti.process_multiple_fields(
            result["data"]["userEdit"]["relationAdd"])

    def delete_membership(self,
                          id: str,
                          group_id: str) -> dict:
        """Removes the user from the given group.

        :param id: User ID to remove from the group.
        :type id: str
        :param group_id: Group ID to remove the user from.
        :type group_id: str
        :return: Representation of the user without sessions or API token
        :rtype: dict
        """
        self.opencti.admin_logger.info("Removing used from group", {
            "id": id, "group_id": group_id})
        query = (
            """
            mutation UserDeleteMembership($id: ID!, $group_id: StixRef!) {
                userEdit(id: $id) {
                    relationDelete(toId: $group_id, relationship_type: "member-of") {
                        """
            + self.properties
            + """
                    }
                }
            }
            """
        )
        result = self.opencti.query(query, {"id": id, "group_id": group_id})
        return self.opencti.process_multiple_fields(
            result["data"]["userEdit"]["relationDelete"])

    def add_organization(self, id: str, organization_id: str) -> Dict:
        """Adds a user to an organization

        :param id: User ID to add to organization
        :type id: str
        :param organization_id: ID of organization to add to
        :type organization_id: str
        :return: Representation of user without sessions or API key
        :rtype: Dict
        """
        self.opencti.admin_logger.info("Adding user to organization", {
            "id": id, "organization_id": organization_id
        })
        query = (
            """
            mutation UserAddOrganization($id: ID!, $organization_id: ID!) {
                userEdit(id: $id) {
                    organizationAdd(organizationId: $organization_id) {
                        """
            + self.properties
            + """
                    }
                }
            }
            """
        )
        result = self.opencti.query(query, {
            "id": id, "organization_id": organization_id})
        return self.opencti.process_multiple_fields(
            result["data"]["userEdit"]["organizationAdd"])

    def delete_organization(self, id: str, organization_id: str) -> Dict:
        """Delete a user from an organization

        :param id: User ID to remove from organization
        :type id: str
        :param organization_id: ID of organization to remove from
        :type organization_id: str
        :return: Representation of user without sessions or API key
        :rtype: Dict
        """
        self.opencti.admin_logger.info("Removing user from organization", {
            "id": id, "organization_id": organization_id
        })
        query = (
            """
            mutation UserDeleteOrganization($id: ID!, $organization_id: ID!) {
                userEdit(id: $id) {
                    organizationDelete(organizationId: $organization_id) {
                        """
            + self.properties
            + """
                    }
                }
            }
            """
        )
        result = self.opencti.query(query, {
            "id": id, "organization_id": organization_id})
        return self.opencti.process_multiple_fields(
            result["data"]["userEdit"]["organizationDelete"])

    def token_renew(self,
                     id: str,
                     include_token: bool = False) -> str:
        """Rotates the API token for the given user

        :param user: User ID to rotate API token for.
        :type user: str
        :param include_token:  Whether to include new API
            token in response from server, defaults to False.
        :type include_token: bool, optional
        :return: API token if include_token else None.
        :rtype: str
        """
        self.opencti.admin_logger.info("Rotating API key for user", {"id": id})
        query = (
            """
            mutation UserRotateToken($id: ID!) {
                userEdit(id: $id) {
                    tokenRenew {
                        """
            + self.properties
            + (self.token_properties if include_token else "")
            + """
                    }
                }
            }
            """
        )
        result = self.opencti.query(query, {"id": id})
        return self.opencti.process_multiple_fields(
            result["data"]["userEdit"]["tokenRenew"])
