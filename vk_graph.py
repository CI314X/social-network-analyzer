import networkx as nx
import requests
import random
from collections import defaultdict
import time


def resolve_url_to_id(vk, url):
    """convert user's url to id***"""

    screen_name = url.split('/')[-1]
    info = vk.method('users.get', {'user_ids': screen_name})[0]
    _id = info['id']
    _is_closed = info['is_closed']
    return _id, _is_closed


class VkGraph():
    def __init__(self, access_token, user_id):
        """user_id - who will be analyzed"""
        self._access_token= access_token
        self.api_version = 5.81
        self.user_id = user_id
        self.users_info = defaultdict(dict)
        self.graph = defaultdict(list)
        
    def request_url(self, method_name, parameters):
        """read https://vk.com/dev/api_requests"""

        req_url = 'https://api.vk.com/method/{method_name}?{parameters}&v={api_v}&access_token={token}'.format(
            method_name=method_name, api_v=self.api_version, parameters=parameters, token=random.choice(self._access_token))

        return req_url
    
    def friends(self, idd):
        """
        read https://vk.com/dev/friends.get
        Принимает идентификатор пользователя
        """
        r = requests.get(self.request_url('friends.get',
                'user_id=%s&fields=uid,first_name,last_name,photo' % idd)).json()
        if 'error' in r.keys():
            print(r)
        else:
            r = r['response']
            self.users_info = {item['id']: item for item in r['items']}
        
    def fast_common_friends(self):
        """
        read https://vk.com/dev/friends.getMutual and read https://vk.com/dev/execute
        Fast make a friend graph
        """
        def parts(lst, n=25):
            """ разбиваем список на части - по 25 в каждой """
            return [lst[i:i + n] for i in range(0, len(lst), n)]
        steps = 0
        for i in parts(list(self.users_info.keys())):
            steps += 1
            # Form code (parameter execute)
            code = 'return {'
            for user_id in i:
                code += f'"{user_id}": API.friends.getMutual({{"source_uid":{self.user_id}, "target_uid":{user_id}}}),'
            code += '};'
            while 1:
                req = requests.get(self.request_url('execute', 'code=%s' % code)).json()
                if 'error' in req.keys():
                    continue
                else:
                    req = req['response'].items()
                    break
            for key, val in req:
                if (int(key) in list(self.users_info.keys())):
                    self.graph[int(key)].append([int(i) for i in val] if val else [])
            if steps % 5 == 0:
                time.sleep(1)
            
        for key in self.graph.keys():
            self.graph[key] = self.graph[key][0]
        self.graph = nx.Graph(self.graph)

    def slow_common_friends(self):
        result = defaultdict(list)
        # users_info = set()
        steps = 0
        for user_id in list(self.users_info.keys()):
            steps += 1
            while 1:
                req = requests.get(self.request_url('friends.get', f'user_id={user_id}')).json()
                if 'error' in req.keys():
                    if req['error']['error_code'] == 15:
                        result[int(user_id)] = []
                        break
                    elif req['error']['error_code'] == 18:
                        break
                    #time.sleep(1)
                    continue
                else:
                    req = req['response']['items']
                    for key in req:
                        if (int(key) in list(self.users_info.keys())):
                            result[int(user_id)].append(int(key))
                    break
            if steps % 5 == 0:
                time.sleep(1)
        self.graph = nx.Graph(result)
    
    def make_graph(self, speed="fast"):
        self.friends(self.user_id)
        if speed == "fast":
            self.fast_common_friends()
        elif speed == "slow":
            self.slow_common_friends()
        else:
            print("Error flag for vk make_graph") # throw
        
        return self.graph, self.users_info
        