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

T_MAX = 0

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
	def __init__(self, vehicle_id, service_type, ID):
		self.service_type = service_type
		self.ID = ID
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

def accumulate_memory(request, servers, S_deliver, finish_time, catch_time):
	if(catch_time >= 10000):
		return
	
	for t in range(finish_time, catch_time):
		servers[S_deliver].memory[t] += request.size

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
		#T = finish_time + wait_vehicle(request, j, finish_time)
		#T_list.append(T)

		index = bisect.bisect_left(servers[j].in_range[request.vehicle_id], finish_time)
		if(index >= len(servers[j].in_range[request.vehicle_id])):
			catch_time = 10000
		else:
			catch_time = servers[j].in_range[request.vehicle_id][index]
		if(catch_time > request.deadline):
			catch_time = 10000

		catch_time_list.append(catch_time)

		

	#request.S_deliver = T_list.index(min(T_list))
	#request.catch_time =  min(T_list)

	request.S_deliver = catch_time_list.index(min(catch_time_list))
	request.catch_time =  catch_time_list[request.S_deliver]
	request.T_deliver = services[request.service_type].T_deliver[request.S_exe][request.S_deliver]

	return request.S_deliver, request.catch_time 

def decide_S_deliver_2(servers, request, finish_compute_time, all_max_memory_use):
	
	T_list = []
	catch_time_list = []


	for j in range(len(servers)):
		T_deliver = services[request.service_type].T_deliver[request.S_exe][j]
		finish_time = finish_compute_time + T_deliver
		#T = finish_time + wait_vehicle(request, j, finish_time)
		#T_list.append(T)

		index = bisect.bisect_left(servers[j].in_range[request.vehicle_id], finish_time)
		if(index >= len(servers[j].in_range[request.vehicle_id])):
			catch_time = 10000
		else:
			catch_time = servers[j].in_range[request.vehicle_id][index]
		if(catch_time > request.deadline):
				all_max_memory_use = 10000

		catch_time_list.append(catch_time)

		

	#request.S_deliver = T_list.index(min(T_list))
	#request.catch_time =  min(T_list)

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
					share_id = request.ID
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
			#TODO: need to come up with a better solution of this part
			#if(T_wait < sorted_queue[i].deadline - sorted_queue[i].T_compute ):
			#	T_wait = np.random.randint(T_wait, sorted_queue[i].deadline - sorted_queue[i].T_compute+1) 

			T_wait = max(T_wait, sorted_queue[i].T_request)
			sorted_queue[i].T_wait = T_wait  
			T_wait += sorted_queue[i].T_compute	
		
	return sorted_queue
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
				all_max_memory_use = 10000
				continue		
			finish_compute_time = request.start_exe_time + request.T_compute
			decide_S_deliver(servers, request, finish_compute_time)


			if(request.catch_time >= T_MAX):
				all_max_memory_use = 100000
				continue
			if((request.catch_time - request.start_exe_time) > request.freshness):
				all_max_memory_use = 100000
				continue
			request.finish_time = finish_compute_time  + services[request.service_type].T_deliver[request.S_exe][request.S_deliver]
			accumulate_memory(request, servers, request.S_deliver, request.finish_time, request.catch_time)

	for server in servers:
		max_memory_use = max(server.memory)
		all_max_memory_use += max_memory_use

	return all_max_memory_use, requests

def find_sol_2(services, requests, servers, T_MAX, servers_modified):
	#refresh the server
	for server in servers:
		server.memory = [0] * T_MAX
	
	all_max_memory_use = 0

	for j in range(len(servers_modified)):
		exe_queue = decide_priority(requests, servers, services, servers_modified[j])
		for request in exe_queue:
			earliest_start_time = request.T_request
			request.start_exe_time = max(earliest_start_time, request.T_wait)
			
			# Constraint (3.2)
			if(request.start_exe_time >= request.deadline):
				all_max_memory_use = 10000
				continue		
			finish_compute_time = request.start_exe_time + request.T_compute
			decide_S_deliver_2(servers, request, finish_compute_time, all_max_memory_use)


			if(request.catch_time >= T_MAX):
				all_max_memory_use = 100000
				continue
			if((request.catch_time - request.start_exe_time) > request.freshness):
				all_max_memory_use = 100000
				continue
			request.finish_time = finish_compute_time  + services[request.service_type].T_deliver[request.S_exe][request.S_deliver]
			
	for request in requests:
		accumulate_memory(request, servers, request.S_deliver, request.finish_time, request.catch_time)

	for server in servers:
		max_memory_use = max(server.memory)
		all_max_memory_use += max_memory_use

	return all_max_memory_use, requests
def pick_neighbor(requests, servers_modified):
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

#find j such that T + C in range 		
def get_init_sol_3():
	for r in range(len(requests)):
		k = requests[r].service_type
		requests[r].S_exe = np.random.randint(0, len(servers))
		for j in range(len(servers)):
			#TC_list.append(services[k].T_request[j] + services[k].T_compute[j])		
			t = services[k].T_request[j] + services[k].T_compute[j]+1
			if(t >= T_MAX):
				continue
			if(vehicles[requests[r].vehicle_id].range[j][t] == 1):
				requests[r].S_exe = j
				# what if j has been assigned too many tasks?
			

		
		#requests[r].S_exe = services[k].T_request.index(min(services[k].T_request))
		servers[requests[r].S_exe].exe_queue.append(r)
		requests[r].T_request = services[k].T_request[requests[r].S_exe]
		requests[r].T_compute = services[k].T_compute[requests[r].S_exe]

#find j such that T + C + Tv in range 
def get_init_sol_4():
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
def get_init_sol_5():
	# each request needs to maintain a possible j list

	for r in range(len(requests)):
		k = requests[r].service_type
		for j in range(len(servers)):
			t = services[k].T_request[j] + services[k].T_compute[j]	
			if(t <= requests[r].freshness and t < requests[r].deadline):
				requests[r].possible_S_exes.append(j)

		#print(len(requests[r].possible_S_exes))
		requests[r].S_exe =  requests[r].possible_S_exes[np.random.randint(0, len(requests[r].possible_S_exes))]
		#requests[r].S_exe = services[k].T_request.index(min(services[k].T_request))
		servers[requests[r].S_exe].exe_queue.append(r)
		requests[r].T_request = services[k].T_request[requests[r].S_exe]
		requests[r].T_compute = services[k].T_compute[requests[r].S_exe]

def pick_neighbor_5(requests):
	a = np.random.randint(0, len(requests))
	servers[requests[a].S_exe].exe_queue.remove(a)
	#requests[a].S_exe = np.random.randint(0, len(servers))
	#requests[a].S_exe = 1
	rand_num = np.random.randint(0, 100)
	if(np.random.randint(0, 100) > -1):
		requests[a].S_exe = requests[a].possible_S_exes[np.random.randint(0, len(requests[a].possible_S_exes))]
	else:
		k = requests[a].service_type
		requests[a].S_exe = services[k].T_request.index(min(services[k].T_request))
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

def read_inputs(services, servers, vehicles, requests):

	num_vehicles = int(input())
	num_servers = int(input())	
	num_services = int(input())

	global T_MAX
	T_MAX = int(input())
	for s in range(num_servers):
		servers.append(Server(s, num_vehicles, T_MAX))
	for i in range(num_vehicles):
		vehicles.append(Vehicle(i, num_servers))
	for k in range(num_services):
		services.append(Service(k, num_servers, num_vehicles))

	for j in range(num_servers):
		tmp = [int(x) for x in input().split()]
		for k in range(num_services):
			services[k].T_request[j] = tmp[k]
			
			#sys.exit()

	for j in range(num_servers):
		T_computes = [int(x) for x in input().split()]
		for k in range(num_services):
			services[k].T_compute[j] = T_computes[k]
	'''
	for k in range(num_services):
		print(services[k].T_compute)
	'''

	for k in range(num_services):
		for j in range(num_servers):
			services[k].T_deliver[j] = [0] * num_servers

	for j in range(num_servers):
		for jj in range(num_servers):
			T_delivers = [int(x) for x in input().split()]
			for k in range(num_services):
				services[k].T_deliver[j][jj] = T_delivers[k]
	'''
	for j in range(num_servers):
		for jj in range(num_servers):
			for k in range(num_services):
				print(services[k].T_deliver[j][jj])   
			print("\n") 
		print("\n") 	
	'''		

	num_requests = 0
	for i in range(num_vehicles):
		deadlines = [int(x) for x in input().split()]
		for k in range(num_services):
			services[k].deadline[i] = deadlines[k]
			if(deadlines[k] != -1):
				requests.append(Request(i, k, num_requests))
				num_requests += 1
	'''
	for k in range(num_services):
		print(services[k].deadline)
	'''

	for i in range(num_vehicles):
		freshnesses = [int(x) for x in input().split()]
		for k in range(num_services):
			services[k].freshness[i] = freshnesses[k]
	

	for i in range(num_vehicles):
		for j in range(num_servers):
			vehicles[i].range[j] = [0] * T_MAX

	
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
			#print(servers[j].in_range[i])
	'''
	for i in range(num_vehicles):
		for j in range(num_servers):
			print(vehicles[i].range[j])
	'''
	#sys.exit()

	sizes = [int(x) for x in input().split()]
	for k in range(num_services):
		services[k].size = sizes[k]
		#print(services[k].size)

	capacities = [int(x) for x in input().split()]
	for j in range(num_servers):
		servers[j].capacity = capacities[j]
		#print(servers[j].capacity)

if __name__ == '__main__':
	start_time = time.time()

	servers = []	
	services = []
	vehicles = []
	requests = []

	servers_modified = []
	#read input file	
	read_inputs(services, servers, vehicles, requests)
	init_requests(requests, services)
	mem = 0
	for request in requests:
		mem += request.size
	#print(mem)
	get_init_sol()
	
	cur_sol, requests = find_sol(services, requests, servers, T_MAX)
	
	best_sol = cur_sol
	best_requests = copy.deepcopy(requests)
	# remind: python passes lists by reference! requests changes, best_requests changes, too 
	# so, use deepcopy to copy by value 

	#print("init_sol = " + str(best_sol))
	#print(best_sol)

	#for request in best_requests: 
		#print(f"{request.vehicle_id} {request.service_type} {request.S_exe} {request.S_deliver} {request.start_exe_time} {request.catch_time}")
	#sys.exit()


	T = 10000
	r = 0.9999
	count = 0
	while T > 1:
		count+= 1
		#init_requests(requests, services)
		pick_neighbor(requests, servers_modified)
		#new_sol, requests = find_sol(services, requests, servers, T_MAX)
		new_sol, requests = find_sol_2(services, requests, servers, T_MAX, servers_modified)
		#print("\n")
		delta_cost = new_sol - cur_sol
		if(delta_cost <= 0):
			cur_sol = new_sol
			if(cur_sol < best_sol):
				best_sol = cur_sol
				best_requests = copy.deepcopy(requests)

				print("best_sol = " + str(best_sol))
				#if(best_sol == 0):
					#print("best")
					#break
		else:
			if(np.random.rand() <= math.exp(- delta_cost / T )):
				cur_sol = new_sol

		if(best_sol < 10000):
			end_time = time.time()
			#break
			
		T *= r

	#print("best_sol = " + str(best_sol))
	print(best_sol)

	for request in best_requests: 
		print(f"{request.vehicle_id} {request.service_type} {request.S_exe} {request.S_deliver} {request.start_exe_time} {request.catch_time}")

	print("count: " + str(count))
	print(f"time: {end_time - start_time}")
	sys.exit()
