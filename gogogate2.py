import requests
import json

"""
    Description:
    ------------
    A very simple module to interface with the GoGoGate2 garage door controller

    This module simply screen-scrapes the php-based web UI for the GoGoGate2 device.

    Usage:
    ------
    >>> import gogogate2
    >>> my_local_ip = '192.168.1.123'
    >>> g = gogogate2.GoGoGate2(my_local_ip,'admin','my_password')
    >>> g.getStatus()
    ['0', '0', '0']
    >>> g.toggleDoor(2)
    True
    >>> g.getStatus()
    ['0', '2', '0']

"""
class GoGoGate2(object):

    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.session_id = None

    """
        Logs in to the GoGoGate2 web app
   
        Sets:
          self.session_id upon success

        Returns:
          True = successful login
          False = failed login
    """   
    def _login(self):
        payload = {"login":self.username,
                   "pass":self.password,
                   "send-login":"Sign+In"}
        r = requests.post(f"http://{self.ip}/index.php", data=payload)
        if r.status_code == 200 and \
           '<input type="submit" class="btn-logout3" name="logout" value=" " title="Logout"/>' in r.text:
            self.session_id = r.cookies['PHPSESSID']
            return True
        return False

    """
        Gets the door status from all 3 doors

        Returns array [a,b,c] where:
          0 = closed, 1 = pulse, 2 = open/opening, 4 = starting?
        Returns None on failed login

        If 200 response but empty response, we assume invalid login
    """
    def _doGetStatus(self):
        cookies = dict(PHPSESSID=self.session_id)
        r = requests.get(f"http://{self.ip}/isg/statusDoorAll.php?status1=10", cookies=cookies)
        if r.status_code == 200 and len(r.text) > 0:
            try:
                return json.loads(r.text)
            except Exception as e:
                return None
        return None

    """
        Attempt a _doGetStatus call.
        If it fails, log in and try again.
    """
    def getStatus(self):
        result = self._doGetStatus()
        if result == None:
            login_result = self._login()
            if login_result == True:
                return self._doGetStatus()
        return result

    """
        Toggles the specified garage door to open or close
      
        Params: door_num = 1, 2 or 3

        Returns:
          True = success
          False = failure / unknown
    """
    def _doToggleDoor(self, door_num):
        cookies = dict(PHPSESSID=self.session_id)
        r = requests.get(f"http://{self.ip}/isg/opendoor.php?numdoor={door_num}", cookies=cookies)
        if r.status_code == 200 and r.text == 'OK':
            return True
        return False

    """
        Attempt a _doToggleDoor call.
        If it fails, log in and try again.
    """
    def toggleDoor(self, door_num):
        result = self._doToggleDoor(door_num)
        if result == False:
            login_result = self._login()
            if login_result == True:
                return self._doToggleDoor(door_num)
        return result
