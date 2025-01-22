from typing import Dict


class Settings:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            standard_id
            entity_type
            parent_types

            platform_organization {
                id, name, description
            }

            platform_title
            platform_favicon
            platform_email
            platform_url
            platform_language

            platform_cluster {
                instances_number
            }

            platform_modules {
                id, enable, running, Warning
            }

            platform_providers {
                name, type, strategy, provider
            }

            platform_user_statuses {
                status, message
            }

            platform_theme
            platform_theme_dark_background
            platform_theme_dark_paper
            platform_theme_dark_nav
            platform_theme_dark_primary
            platform_theme_dark_secondary
            platform_theme_dark_accent
            platform_theme_dark_logo
            platform_theme_dark_logo_collapsed
            platform_theme_dark_logo_login
            platform_theme_light_background
            platform_theme_light_paper
            platform_theme_light_nav
            platform_theme_light_primary
            platform_theme_light_secondary
            platform_theme_light_accent
            platform_theme_light_logo
            platform_theme_light_logo_collapsed
            platform_theme_light_logo_login
            platform_map_tile_server_dark
            platform_map_tile_server_light

            platform_openbas_url
            platform_openbas_disable_display

            platform_openerm_url
            platform_openmtd_url

            platform_ai_enabled
            platform_ai_type
            platform_ai_model
            platform_ai_has_token

            platform_login_message
            platform_consent_message
            platform_consent_confirm_text

            platform_banner_text
            platform_banner_level

            platform_session_idle_timeout
            platform_session_timeout

            platform_whitemark
            platform_demo
            platform_reference_attachment

            platform_feature_flags {
                id, enable, running, warning
            }

            platform_critical_alerts {
                message, type
                details {
                    groups {
                        id, name, description
                    }
                }
            }

            platform_trash_enabled

            platform_protected_sensitive_config {
                enabled
                markings {
                    enabled, protected_ids
                }
                groups {
                    enabled, protected_ids
                }
                roles {
                    enabled, protected_ids
                }
                rules {
                    enabled, protected_ids
                }
                ce_ee_toggle {
                    enabled, protected_ids
                }
                file_indexing {
                    enabled, protected_ids
                }
                platform_organization {
                    enabled, protected_ids
                }
            }

            created_at
            updated_at
            enterprise_edition
            analytics_google_analytics_v4

            activity_listeners {
                id, name, entity_type
            }
        """
        self.messages_properties = """
            platform_messages {
                id, message, activated, dismissible, update_at, color
                recipients {
                    id, name, entity_type
                }
            }
            messages_administration {
                id, message, activated, dismissible, update_at, color
                recipients {
                    id, name, entity_type
                }
            }
        """
        self.password_policy_properties = """
            otp_mandatory
            password_policy_min_length
            password_policy_max_length
            password_policy_min_symbols
            password_policy_min_numbers
            password_policy_min_words
            password_policy_min_lowercase
            password_policy_min_uppercase
        """

    def create(self, **kwargs) -> Dict:
        """Stub function for tests

        :return: Settings as defined by self.read()
        :rtype: Dict
        """
        self.opencti.admin_logger.info(
            "Settings.create called with arguments", kwargs)
        raise Exception
        return self.read()

    def delete(self, **kwargs):
        """Stub function for tests"""
        self.opencti.admin_logger.info(
            "Settings.delete called with arguments", kwargs)
        raise Exception

    def read(self, **kwargs) -> Dict:
        pass

    def update_field(self, **kwargs) -> Dict:
        pass

    def edit_message(self, **kwargs) -> Dict:
        pass

    def delete_message(self, **kwargs) -> Dict:
        pass
