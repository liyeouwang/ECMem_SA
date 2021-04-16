'''
(Li-Yeou) Try different initial solutions
(Li-Yeou) Report when to find the first feasible solution
You initial solutions should lead earlier time finding the first feasible solution

prune and search?

#TODO: 
Deal with M_bar problem
Add sorting function
Need to come up with a better solution to deciding T_wait
Each server maintain a vehicle arrival time table (not use for loop to find out when catching)
'''

import numpy as np
import math 
import sys
import copy
import time
import bisect
import matplotlib.pyplot as plt

config = {
    "LARGE_NUM": 1000000,

    #Method to obtain initail solution
    #"GET_INITIAL": 2,
    "CREATE_PLOT_FILE": True,
    "PLOT_FILE": "plot/test1_init4.out",

    #Simulated annealing parameters
    "T": 1000000,
    "r": 0.9999
    

}


'''
    --------------------------------------------------------------------
    This part define T.
    
'''


class Vehicle:
	def __init__(self, vehicle_id, num_servers): 
		self.vehicle_id = vehicle_id
		self.range = [0] * num_servers

class Service:
	def __init__(self, service_type, num_servers, num_vehicles
		):		
		self.service_type = service_type
		self.size = 0
		self.deadline = [0] * num_vehicles
		self.freshness = [0] * num_vehicles
		self.T_request = [0] * num_servers
		self.T_deliver = [0] * num_servers
		self.T_compute = [0] * num_servers

class Server:
	def __init__(self, server_id, num_vehicles, T_MAX):
		self.server_id = server_id
		self.memory = [0] * T_MAX
		self.capacity = 0
		self.exe_queue = []
		self.in_range = [0] * num_vehicles

class Request:
	def __init__(self, vehicle_id, service_type, request_id):
		self.service_type = service_type
		self.request_id = request_id
		self.vehicle_id = vehicle_id
		self.deadline = 0	
		self.T_request = 0
		self.T_compute = 0
		self.T_deliver = -1
		self.freshness = -1
		self.shared = False
		self.shared_with = -1
		self.size = 0
		self.S_exe = 0
		self.S_deliver = 0
		self.T_wait = 0
		self.start_exe_time = 0
		self.catch_time = -1
		self.possible_S_exes = []
		self.finish_time = -1


def check_feasibility(requests):
	for request in requests:
		if((request.start_exe_time >= request.deadline) or (request.catch_time >=T_MAX)  or (request.catch_time - request.start_exe_time > request.freshness)):
			return False
	return True

#def accumulate_memory(request, servers, S_deliver, finish_time, catch_time):
def accumulate_memory(request):
	if(request.catch_time >= 10000):
		return
	
	for t in range(request.finish_time, request.catch_time):
		servers[request.S_deliver].memory[t] += request.size

def wait_vehicle(request, S_deliver, finish_time):
	T_wait_vehicle = 0
	is_delivery = False


	# Constraint (3.3)
	# Constraint (3.4)
	# Constraint (3.6)
	for t in range(finish_time, min(T_MAX, request.deadline+1)):
		T_wait_vehicle = t - finish_time
		if(vehicles[request.vehicle_id].range[S_deliver][t] == 1):
			is_delivery = True
			break

	if(is_delivery == False):
		T_wait_vehicle = 100000

	return T_wait_vehicle


def decide_S_deliver(servers, request, finish_compute_time):
	
	T_list = []
	catch_time_list = []


	for j in range(len(servers)):
		T_deliver = services[request.service_type].T_deliver[request.S_exe][j]
		finish_time = finish_compute_time + T_deliver

		index = bisect.bisect_left(servers[j].in_range[request.vehicle_id], finish_time)
		if(index >= len(servers[j].in_range[request.vehicle_id])):
			catch_time = T_MAX + 1
		else:
			catch_time = servers[j].in_range[request.vehicle_id][index]
		if(catch_time > request.deadline):
			catch_time = T_MAX + 1

		catch_time_list.append(catch_time)

	request.S_deliver = catch_time_list.index(min(catch_time_list))
	request.catch_time =  catch_time_list[request.S_deliver]
	request.T_deliver = services[request.service_type].T_deliver[request.S_exe][request.S_deliver]

	return request.S_deliver, request.catch_time 

def decide_priority(requests, servers, services, S_exe):

	queue = []
	for r in servers[S_exe].exe_queue:
		queue.append(requests[r])
		
	for request in queue:
		if(request.deadline > T_MAX-1):
			request.deadline = T_MAX-1

	'''
	#TODO: need a sorting funcion
	sort first by deadline, then by size
	'''
	#sorted_queue = sorted(queue, key=lambda x: x.deadline) #should be size or deadline?
	#sorted_queue = sorted(queue, key=lambda x: x.size)
	sorted_queue = sorted(queue, key = lambda x: (x.deadline, x.size)) #if same deadline, sort size ??

	for request in sorted_queue:
		request.shared = False

	for service_type in range(len(services)):
		appeared = False
		share_id = -1
		for request in sorted_queue:
			if(request.service_type == service_type):
				if(appeared == False):
					appeared = True
					share_id = request.request_id
				else:
					request.shared_with = share_id
					request.shared = True

	#T_wait = 0
	if(len(sorted_queue) > 0):
		T_wait = sorted_queue[0].T_request
	for i in range(len(sorted_queue)):
		if(sorted_queue[i].shared == True):
			sorted_queue[i].T_wait = requests[sorted_queue[i].shared_with].T_wait
		else:
			#TODO: need to come up with a better solution for this part
			#if(T_wait < sorted_queue[i].deadline - sorted_queue[i].T_compute ):
			#	T_wait = np.random.randint(T_wait, sorted_queue[i].deadline - sorted_queue[i].T_compute+1) 

			T_wait = max(T_wait, sorted_queue[i].T_request)
			sorted_queue[i].T_wait = T_wait  
			T_wait += sorted_queue[i].T_compute	
		
	return sorted_queue

def calculate_max_memory_use():
	all_max_memory_use = 0
	for request in requests:
		accumulate_memory(request)

	for server in servers:
		max_memory_use = max(server.memory)
		all_max_memory_use += max_memory_use
	return all_max_memory_use

def find_sol(services, requests, servers, T_MAX):
	#refresh the server
	for server in servers:
		server.memory = [0] * T_MAX
	
	all_max_memory_use = 0

	for j in range(len(servers)):
		exe_queue = decide_priority(requests, servers, services, j)
		for request in exe_queue:
			earliest_start_time = request.T_request
			request.start_exe_time = max(earliest_start_time, request.T_wait)
			
			# Constraint (3.2)
			if(request.start_exe_time >= request.deadline):
				all_max_memory_use = 10000000
				continue		
			finish_compute_time = request.start_exe_time + request.T_compute
			decide_S_deliver(servers, request, finish_compute_time)


			if(request.catch_time >= T_MAX):
				all_max_memory_use = 1000000000
				continue
			if((request.catch_time - request.start_exe_time) > request.freshness):
				all_max_memory_use = 1000000000
				continue
			request.finish_time = finish_compute_time  + services[request.service_type].T_deliver[request.S_exe][request.S_deliver]
			#accumulate_memory(request, servers, request.S_deliver, request.finish_time, request.catch_time)
			accumulate_memory(request)

	for server in servers:
		max_memory_use = max(server.memory)
		all_max_memory_use += max_memory_use

	return all_max_memory_use, requests


#def find_sol_2(services, requests, servers, T_MAX, servers_modified):
def find_sol_2():
	#refresh the server
	for server in servers:
		server.memory = [0] * T_MAX
	
	#all_max_memory_use = 0

	for j in range(len(servers_modified)):
		exe_queue = decide_priority(requests, servers, services, servers_modified[j])
		for request in exe_queue:
			earliest_start_time = request.T_request
			request.start_exe_time = max(earliest_start_time, request.T_wait)
			finish_compute_time = request.start_exe_time + request.T_compute
			decide_S_deliver(servers, request, finish_compute_time)
			request.finish_time = finish_compute_time  + services[request.service_type].T_deliver[request.S_exe][request.S_deliver]
			

	is_feasible = check_feasibility(requests)
	if(is_feasible == False):
		all_max_memory_use = config["LARGE_NUM"]
		return all_max_memory_use, requests

	else:
		all_max_memory_use = calculate_max_memory_use()

	return all_max_memory_use, requests
def pick_neighbor(requests, servers_modified):
#def pick_neighbor(requests, servers):
	a = np.random.randint(0, len(requests))

	servers_modified.clear()
	servers_modified.append(requests[a].S_exe)
	servers[requests[a].S_exe].exe_queue.remove(a)
	#requests[a].S_exe = np.random.randint(0, len(servers))
	#requests[a].S_exe = 1
	rand_num = np.random.randint(0, 100)
	if(np.random.randint(0, 100) > 50):
		requests[a].S_exe = np.random.randint(0, len(servers))
	else:
		k = requests[a].service_type
		requests[a].S_exe = services[k].T_request.index(min(services[k].T_request))
	servers_modified.append(requests[a].S_exe)
	requests[a].T_request = services[requests[a].service_type].T_request[requests[a].S_exe]
	servers[requests[a].S_exe].exe_queue.append(a)
	requests[a].T_compute = services[requests[a].service_type].T_compute[requests[a].S_exe]

#origin
def get_init_sol():
	servers_modified.clear()
	for s in range(len(servers)):
		servers_modified.append(s)

	for r in range(len(requests)):
		k = requests[r].service_type
		#requests[r].S_exe = 1
		if(np.random.randint(0, 100) > -1):
			requests[r].S_exe = np.random.randint(0, len(servers))
		else:
			#print(services[k].T_request)
			requests[r].S_exe = services[k].T_request.index(min(services[k].T_request))
			#sys.exit()
		#requests[r].S_exe = services[k].T_request.index(min(services[k].T_request))
		servers[requests[r].S_exe].exe_queue.append(r)
		requests[r].T_request = services[k].T_request[requests[r].S_exe]
		requests[r].T_compute = services[k].T_compute[requests[r].S_exe]

#find j such that T is minimum
def get_init_sol_1():
	servers_modified.clear()
	for s in range(len(servers)):
		servers_modified.append(s)

	for r in range(len(requests)):
		k = requests[r].service_type
		#requests[r].S_exe = 1
		if(np.random.randint(0, 100) > 100):
			requests[r].S_exe = np.random.randint(0, len(servers))
		else:
			#print(services[k].T_request)
			requests[r].S_exe = services[k].T_request.index(min(services[k].T_request))
			#sys.exit()
		#requests[r].S_exe = services[k].T_request.index(min(services[k].T_request))
		servers[requests[r].S_exe].exe_queue.append(r)
		requests[r].T_request = services[k].T_request[requests[r].S_exe]
		requests[r].T_compute = services[k].T_compute[requests[r].S_exe]

#find j such that T + C is minimum
def get_init_sol_2():
	servers_modified.clear()
	for s in range(len(servers)):
		servers_modified.append(s)

	for r in range(len(requests)):
		k = requests[r].service_type
		TC_list = []
		for j in range(len(servers)):
			TC_list.append(services[k].T_request[j] + services[k].T_compute[j])		
		requests[r].S_exe = TC_list.index(min(TC_list))
		#requests[r].S_exe = services[k].T_request.index(min(services[k].T_request))
		servers[requests[r].S_exe].exe_queue.append(r)
		requests[r].T_request = services[k].T_request[requests[r].S_exe]
		requests[r].T_compute = services[k].T_compute[requests[r].S_exe]

#find j such that T + C + Tv in range 
def get_init_sol_4():
	servers_modified.clear()
	for s in range(len(servers)):
		servers_modified.append(s)

	for r in range(len(requests)):
		k = requests[r].service_type
		requests[r].S_exe = np.random.randint(0, len(servers))
		for j in range(len(servers)):
			for jj in range(len(servers)):
				t = services[k].T_request[j] + services[k].T_compute[j] + services[k].T_deliver[j][jj]
				if(t < T_MAX):
					if(vehicles[requests[r].vehicle_id].range[j][t] == 1):
						requests[r].S_exe = j
						#print("hi")
				#else prune this j? 


		servers[requests[r].S_exe].exe_queue.append(r)
		requests[r].T_request = services[k].T_request[requests[r].S_exe]
		requests[r].T_compute = services[k].T_compute[requests[r].S_exe]

#prune j whose T + C > freshness or deadline
def get_init_sol_3():
	servers_modified.clear()
	for s in range(len(servers)):
		servers_modified.append(s)

	# each request needs to maintain a possible j list

	for r in range(len(requests)):
		k = requests[r].service_type
		for j in range(len(servers)):
			t = services[k].T_request[j] + services[k].T_compute[j]	
			if((services[k].T_compute[j] <= requests[r].freshness) and (t < requests[r].deadline)):
				requests[r].possible_S_exes.append(j)

		#print(len(requests[r].possible_S_exes))
		requests[r].S_exe =  requests[r].possible_S_exes[np.random.randint(0, len(requests[r].possible_S_exes))]
		#requests[r].S_exe = services[k].T_request.index(min(services[k].T_request))
		servers[requests[r].S_exe].exe_queue.append(r)
		requests[r].T_request = services[k].T_request[requests[r].S_exe]
		requests[r].T_compute = services[k].T_compute[requests[r].S_exe]

def pick_neighbor_3(requests):
	a = np.random.randint(0, len(requests))
	#servers_modified.clear()
	#servers_modified.append(requests[a].S_exe)
	servers[requests[a].S_exe].exe_queue.remove(a)

	rand_num = np.random.randint(0, 100)
	if(np.random.randint(0, 100) > -1):
		requests[a].S_exe = requests[a].possible_S_exes[np.random.randint(0, len(requests[a].possible_S_exes))]
	else:
		k = requests[a].service_type
		requests[a].S_exe = services[k].T_request.index(min(services[k].T_request))
	#servers_modified.append(requests[a].S_exe)
	requests[a].T_request = services[requests[a].service_type].T_request[requests[a].S_exe]
	servers[requests[a].S_exe].exe_queue.append(a)
	requests[a].T_compute = services[requests[a].service_type].T_compute[requests[a].S_exe]

def init_requests(requests, services):
	for request in requests:
		k = request.service_type
		i = request.vehicle_id
		request.deadline = services[k].deadline[i]
		request.freshness = services[k].freshness[i]
		request.size = services[k].size
		#requests.T_request = services[k].T_request[requests[r].S_exe]
		#requests[r].T_compute = services[k].T_compute[requests[r].S_exe]
		request.T_deliver = -1
		request.shared = False
		request.shared_with = -1
		#request.S_exe = -1
		#request.S_deliver = -1
		request.T_wait = -1
		request.catch_time = -1
	#sys.exit()

#def read_inputs(services, servers, vehicles, requests):
def read_inputs():

	num_vehicles = int(input())
	num_servers = int(input())	
	num_services = int(input())

	global T_MAX
	T_MAX = int(input())

	# number of servers J
	for j in range(num_servers):
		servers.append(Server(j, num_vehicles, T_MAX))

	# number of vehicles I
	for i in range(num_vehicles):
		vehicles.append(Vehicle(i, num_servers))

	# number of services K
	for k in range(num_services):
		services.append(Service(k, num_servers, num_vehicles))

	# earliest start-execution time of service k in server j (T)
	for j in range(num_servers):
		tmp = [int(x) for x in input().split()]
		for k in range(num_services):
			services[k].T_request[j] = tmp[k]

	# computation time of service k in server j (C)
	for j in range(num_servers):
		T_computes = [int(x) for x in input().split()]
		for k in range(num_services):
			services[k].T_compute[j] = T_computes[k]

	# delivery time of service k from server j to server jj (Tv)
	for k in range(num_services):
		for j in range(num_servers):
			services[k].T_deliver[j] = [0] * num_servers
	for j in range(num_servers):
		for jj in range(num_servers):
			T_delivers = [int(x) for x in input().split()]
			for k in range(num_services):
				services[k].T_deliver[j][jj] = T_delivers[k]	

	# deadline of service k for vehicle i 
	num_requests = 0
	for i in range(num_vehicles):
		deadlines = [int(x) for x in input().split()]
		for k in range(num_services):
			services[k].deadline[i] = deadlines[k]
			if(deadlines[k] != -1):
				requests.append(Request(i, k, num_requests))
				num_requests += 1

	# freshness of service k for vehicle i 
	for i in range(num_vehicles):
		freshnesses = [int(x) for x in input().split()]
		for k in range(num_services):
			services[k].freshness[i] = freshnesses[k]
	
	# if vehicle i is in the covering range of server j (0 or 1)
	for i in range(num_vehicles):
		for j in range(num_servers):
			vehicles[i].range[j] = [0] * T_MAX

	#
	for j in range(num_servers):
		for i in range(num_vehicles):
			servers[j].in_range[i] = []

	for i in range(num_vehicles):
		for j in range(num_servers):
			ranges = [int(x) for x in input().split()]
			
			for t in range(T_MAX):
				vehicles[i].range[j][t] = ranges[t]
				if(ranges[t] == 1):
					servers[j].in_range[i].append(t)

	sizes = [int(x) for x in input().split()]
	for k in range(num_services):
		services[k].size = sizes[k]

	capacities = [int(x) for x in input().split()]
	for j in range(num_servers):
		servers[j].capacity = capacities[j]

if __name__ == '__main__':
	#random seed
	np.random.seed(1)

	start_time = time.time()

	T_MAX = 0
	servers = []	
	services = []
	vehicles = []
	requests = []
	servers_modified = []

	#read input file
	read_inputs()	
	#read_inputs(services, servers, vehicles, requests)

	#initailize some parameters 
	init_requests(requests, services)

	get_init_sol_4()
	end_time = time.time()
	print(f"time: {end_time - start_time}")
	#cur_sol, requests = find_sol(services, requests, servers, T_MAX)
	cur_sol, requests = find_sol_2()

	best_sol = cur_sol
	best_requests = copy.deepcopy(requests)
	# remind: python passes lists by reference! requests changes, best_requests changes, too 
	# so, use deepcopy to copy by value 
	print("init_sol = " + str(best_sol))


	T = config["T"]
	r = config["r"]
	count = 0
	counts = []
	sols = []
	while T > 1:
		count+= 1
		#pick_neighbor_3(requests)
		pick_neighbor(requests, servers_modified)
		#new_sol, requests = find_sol(services, requests, servers, T_MAX)
		#new_sol, requests = find_sol_2(services, requests, servers, T_MAX, servers_modified)
		new_sol, requests = find_sol_2()
		#print("\n")
		delta_cost = new_sol - cur_sol
		if(delta_cost <= 0):
			cur_sol = new_sol
			if(cur_sol < best_sol):
				
				best_sol = cur_sol
				best_requests = copy.deepcopy(requests)

				print("best_sol = " + str(best_sol))
				
				if(best_sol == 0):
					#sys.exit()
					#print("best")
					break
		else:
			if(np.random.rand() <= math.exp(- delta_cost / T )):
				cur_sol = new_sol

		if(best_sol < 10000):
			sols.append(best_sol)
			counts.append(count)

			

			
		T *= r

	#print("best_sol = " + str(best_sol))
	print(best_sol)

	for request in best_requests: 
		print(f"{request.vehicle_id} {request.service_type} {request.S_exe} {request.S_deliver} {request.start_exe_time} {request.catch_time}")

	print("count: " + str(count))
	#print(f"time: {end_time - start_time}")

	if(config['CREATE_PLOT_FILE'] == True):	
		out_file = open(config['PLOT_FILE'], "w")
		for i in range(len(sols)):
			out_file.write(f"{counts[i]} {sols[i]}")
			out_file.write("\n")

	#plt.plot(counts, sols)
	#plt.show()
	#sys.exit()
