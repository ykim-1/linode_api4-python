from __future__ import absolute_import

from linode.errors import UnexpectedResponseError
from linode.objects import Base, Property

from .whitelist_entry import WhitelistEntry


class Profile(Base):
    api_endpoint = "/profile"
    id_attribute = 'username'

    properties = {
        'username': Property(identifier=True),
        'email': Property(mutable=True),
        'timezone': Property(mutable=True),
        'email_notifications': Property(mutable=True),
        'referrals': Property(),
        'ip_whitelist_enabled': Property(mutable=True),
        'lish_auth_method': Property(mutable=True),
        'authorized_keys': Property(mutable=True),
        'two_factor_auth': Property(),
        'restricted': Property(),
    }

    def reset_password(self, password):
        """
        Resets the password of the token's user.
        """
        result = self._client.post('/profile/password', data={ "password": password })

        return result

    def enable_tfa(self):
        """
        Enables TFA for the token's user.  This requies a follow-up request
        to confirm TFA.  Returns the TFA secret that needs to be confirmed.
        """
        result = self._client.post('/profile/tfa-enable')

        return result['secret']

    def confirm_tfa(self, code):
        """
        Confirms TFA for an account.  Needs a TFA code generated by enable_tfa
        """
        result = self._client.post('/profile/tfa-enable-confirm', data={
            "tfa_code": code
        })

        return True

    def disable_tfa(self):
        """
        Turns off TFA for this user's account.
        """
        result = self._client.post('/profile/tfa-disable')

        return True

    @property
    def grants(self):
        """
        Returns grants for the current user
        """
        from linode.objects.account import UserGrants
        resp = self._client.get('/profile/grants') # use special endpoint for restricted users

        grants = UserGrants(self._client, self.username, resp)
        return grants

    @property
    def whitelist(self):
        """
        Returns the user's whitelist entries, if whitelist is enabled
        """
        return self._client._get_and_filter(WhitelistEntry)

    def add_whitelist_entry(self, address, netmask, note=None):
        """
        Adds a new entry to this user's IP whitelist, if enabled
        """
        result = self._client.post("{}/whitelist".format(Profile.api_endpoint),
                data={
                    "address": address,
                    "netmask": netmask,
                    "note": note,
        })

        if not 'id' in result:
            raise UnexpectedResponseError("Unexpected response creating whitelist entry!")

        return WhitelistEntry(result['id'], self._client, json=result)
