import numpy as np
import math 
import sys

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
class Request:
	def __init__(self, vehicle_id, service_type, ID):
		self.service_type = service_type
		self.ID = ID
		self.vehicle_id = vehicle_id
		self.deadline = 0	
		self.T_request = 0
		self.T_compute = 0
		self.T_deliver = 0
		self.shared = False
		self.shared_with = -1
		self.size = 0
		self.S_exe = 0
		self.S_deliver = 0
		self.T_wait = 0
		self.catch_time = 0


def accumulate_memory(request, servers, S_deliver, finish_time, catch_time):

	#if(catch_time < 100000):
	#print("request.ID: " + str(request.ID) + " finish_time: " + str(finish_time) + " catch_time: " + str(catch_time))
	if(catch_time >= 10000):
		return
		#catch_time = T_MAX-1
		#request.size = 100
		#print("hi")

	
	for t in range(finish_time, catch_time):
		#print("request.size: "+ str(request.size))
		servers[S_deliver].memory[t] += request.size
	#print("servers[" + str(S_deliver) + "].memory: " + str(servers[S_deliver].memory))

def wait_vehicle(request, S_deliver, finish_time):
	T_wait_vehicle = 0
	is_delivery = False
	
	#print("finish_time: " + str(finish_time))
	#if(finish_time < T_MAX):
	#	print("finish_time: " + str(finish_time))
	#	print(vehicles[request.vehicle_id].range[S_deliver])
	#	print(vehicles[request.vehicle_id].range[S_deliver][finish_time])
	#print("request.ID: " + str(request.ID) + " S_deliver: " + str(S_deliver))
	#print("request.vehicle_id: " + str(request.vehicle_id) + " S_deliver: " + str(S_deliver))
	for t in range(finish_time, T_MAX):
		T_wait_vehicle = t - finish_time
		if(vehicles[request.vehicle_id].range[S_deliver][t] == 1):
			#print("request "+str(request.ID) + "vehicles["+ str(request.vehicle_id) +"].range["+str(S_deliver)+"]["+str(t)+"] == 1")
			is_delivery = True

			#print("catch")
			break
		#else:
			#servers[S_deliver].memory[t] += request.size

	if(is_delivery == False):
		T_wait_vehicle = 100000

	#print("request.ID: " + str(request.ID) + " finish_time: " + str(finish_time) + " T_wait_vehicle: " + str(T_wait_vehicle))
	return T_wait_vehicle

def decide_S_deliver(servers, request, finish_compute_time):
	
	T_list = []

	for j in range(len(servers)):
		#print("finish_compute_time: " + str(finish_compute_time))
		T_deliver = services[request.service_type].T_deliver[request.S_exe][j]
		#print("request.ID: " + str(request.ID) + " finish_compute_time: " + str(finish_compute_time))
		finish_time = finish_compute_time + T_deliver
		#print("finish_time: " + str(finish_time))
		#print("request.ID: " + str(request.ID) + " finish_time: " + str(finish_time))
		T = finish_time + wait_vehicle(request, j, finish_time)
		T_list.append(T)
		#print("request.ID: " + str(request.ID) + " T: " + str(T))

	request.S_deliver = T_list.index(min(T_list))
	#print("request "+str(request.ID) + "T_list: " + str(T_list))
	request.catch_time =  min(T_list)
	request.T_deliver = services[request.service_type].T_deliver[request.S_exe][request.S_deliver]

	return request.S_deliver, request.catch_time 

def decide_priority_2(requests, servers, services, S_exe):

	queue = []
	for r in servers[S_exe].exe_queue:
		queue.append(requests[r])
		
	#for request in queue:
	#	if(request.deadline > T_MAX):
	#		request.deadline = T_MAX
	#sorted_queue = sorted(queue, key=lambda x: x.size) #should be size or deadline?
	sorted_queue = sorted(queue, key=lambda x: x.deadline)
	#sorted_queue = sorted(queue, key = lambda x: (x.deadline, x.size)) #if same deadline, sort size 

	for request in sorted_queue:
		request.shared = False

	for service_type in range(len(services)):
		appeared = False
		share_id = -1
		for request in sorted_queue:
			#print("S_exe: " + str(S_exe) + "request "+str(request.ID)+ "request.service_type: " + str(request.service_type) + "service_type " + str(service_type))
			if(request.service_type == service_type):
				if(appeared == False):
					#print("appeared == False")
					appeared = True
					share_id = request.ID
				else:
					request.shared_with = share_id
					request.shared = True
				#print("S_exe: " + str(S_exe) + "request "+str(request.ID) + " service_type: " + str(service_type) + " share: " + str(request.shared))


	T_wait = 0
	for i in range(len(sorted_queue)):
		if(sorted_queue[i].shared == True):
			sorted_queue[i].T_wait = requests[sorted_queue[i].shared_with].T_wait
			#print("S_exe: " + str(S_exe) + "request "+str(sorted_queue[i].ID) + " shared with request " + str(sorted_queue[i].shared_with))
		else:
			if(T_wait < sorted_queue[i].deadline - sorted_queue[i].T_compute ):
				'''
				if(S_exe == 0):
					T_wait = 35
				else:
					T_wait = 36
				'''
				T_wait = np.random.randint(T_wait, sorted_queue[i].deadline - sorted_queue[i].T_compute) 
				#print("sorted_queue[i].deadline: " + str(sorted_queue[i].deadline))
				#print("T_wait: "+ str(T_wait))
			#sys.exit()
			#sorted_queue[i].priority = i 
			sorted_queue[i].T_wait = T_wait  
			T_wait += sorted_queue[i].T_compute

		
		#print("S_exe: " + str(S_exe) + " request.ID: " + str(sorted_queue[i].ID) + " T_wait: " + str(sorted_queue[i].T_wait))
		#print("S_exe: " + str(S_exe) + "sorted_queue[i].priority: " + str(sorted_queue[i].priority))

		#print("S_exe: " + str(S_exe) + "sorted_queue[i].T_compute: " + str(sorted_queue[i].T_compute))

	#for service in sorted_queue:
	#	if(service.T_wait != 0):
	#		print("service.T_wait" + str(service.T_wait))
	
	return sorted_queue
def find_sol_2(services, requests, servers, T_MAX):

	#refresh the server
	for server in servers:
		server.memory = [0] * T_MAX
	
	all_max_memory_use = 0

	for j in range(len(servers)):
		exe_queue = decide_priority_2(requests, servers, services, j)
		for request in exe_queue:
			S_exe = request.S_exe
			earliest_start_time = request.T_request
			start_exe_time = earliest_start_time + request.T_wait
			#print("start_exe_time: " + str(start_exe_time) + "deadline: " + str(request.deadline))
			if(start_exe_time >= request.deadline):
				#print("out")
				all_max_memory_use = 10000
				continue		
			finish_compute_time = start_exe_time + request.T_compute
			S_deliver, catch_time = decide_S_deliver(servers, request, finish_compute_time)
			if(catch_time >= T_MAX):
				all_max_memory_use = 10000
			#print("request.ID: " + str(request.ID) + " S_deliver: " + str(S_deliver))
			finish_time = finish_compute_time  + services[request.service_type].T_deliver[S_exe][S_deliver]
			#print("finish_time: " + str(finish_time) + " catch_time: " + str(catch_time))
			#print("finish_time: " + str(finish_time))
			accumulate_memory(request, servers, S_deliver, finish_time, catch_time)
	#sum up memory usage 

	#for request in requests:
		#print("request " + str(request.ID) + " S_exe: " + str(request.S_exe) + " S_deliver: " + str(request.S_deliver))
	#print("\n")

	for server in servers:
		#print("server.memory: " + str(server.memory))
		max_memory_use = max(server.memory)
		#print("max_memory_use: " + str(max_memory_use))
		all_max_memory_use += max_memory_use
		#print(all_max_memory_use)
	return all_max_memory_use, requests
def pick_neighbor_2(requests):
	a = np.random.randint(0, len(requests))
	servers[requests[a].S_exe].exe_queue.remove(a)
	requests[a].S_exe = np.random.randint(0, len(servers))
	requests[a].T_request = services[requests[a].service_type].T_request[requests[a].S_exe]
	servers[requests[a].S_exe].exe_queue.append(a)
	requests[a].T_compute = services[requests[a].service_type].T_compute[requests[a].S_exe]
def get_init_sol(requests):
	for r in range(len(requests)):
		k = requests[r].service_type
		requests[r].S_exe = 0

		servers[requests[r].S_exe].exe_queue.append(r)
		#requests[r].S_deliver = 0
		requests[r].T_request = services[k].T_request[requests[r].S_exe]
		requests[r].T_compute = services[k].T_compute[requests[r].S_exe]
		#print("requests[r].T_request: " + str(requests[r].T_request))
		#print("requests[r].S_deliver: " + str(requests[r].S_deliver))

def init_requests(requests, services):
	for request in requests:
		k = request.service_type
		i = request.vehicle_id
		request.deadline = services[k].deadline[i]
		request.freshness = services[k].freshness[i]
		request.size = services[k].size
		#print("request.size " + str(request.size ))
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
	'''
	for k in range(num_services):
		print(services[k].freshness)
	'''

	for i in range(num_vehicles):
		for j in range(num_servers):
			vehicles[i].range[j] = [0] * T_MAX

	for i in range(num_vehicles):
		for j in range(num_servers):
			ranges = [int(x) for x in input().split()]
			for t in range(T_MAX):
				vehicles[i].range[j][t] = ranges[t]
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


	

	'''
	input_file = open("input.txt")
	
	#num_servers = int(input_file.readline())
	

	#service 
	num_services = int(input_file.readline())
	for k in range(num_services):		
		line = input_file.readline().split()

		#vehicle_id, service_type, size, deadline
		service = Service(int(line[0]), int(line[1]), int(line[2]), int(line[3]))
		
		line = input_file.readline()
		service.T_request = [int(i) for i in line.split()]

		line = input_file.readline()
		service.T_compute = [int(i) for i in line.split()]

		line = input_file.readline()
		service.T_deliver = [int(i) for i in line.split()]

		services.append(service)

	input_file.close()

	input_file = open("paths.txt")
	num_vehicles = int(input_file.readline())
	for v in range(num_vehicles):
		vehicle_id = int(input_file.readline())
		for s in range(num_servers):
			line = input_file.readline().split()
			servers[s].t_vehicle_arrive[vehicle_id] = int(line[0])
			servers[s].t_vehicle_leave[vehicle_id] = int(line[1])
			
	input_file.close()
	'''

if __name__ == '__main__':

	

	servers = []	
	services = []
	vehicles = []
	requests = []
	#read input file	
	read_inputs(services, servers, vehicles, requests)
	#print("T_MAX: " + str(T_MAX))
	init_requests(requests, services)
	get_init_sol(requests)
	
	cur_sol, requests = find_sol_2(services, requests, servers, T_MAX)
	
	best_sol = cur_sol
	best_requests = requests
	#print("init_sol = " + str(best_sol))
	#sys.exit()
	#print("\n")

	T = 100000
	r = 0.999
	count = 0
	while T > 1:
		count+= 1
		pick_neighbor_2(requests)
		new_sol, requests = find_sol_2(services, requests, servers, T_MAX)
		#print("\n")
		delta_cost = new_sol - cur_sol
		if(delta_cost <= 0):
			cur_sol = new_sol
			if(cur_sol < best_sol):
				best_sol = cur_sol
				best_requests = requests
				#print("best_sol = " + str(best_sol))
				#if(best_sol == 0):
				#	sys.exit()
		else:
			if(np.random.rand() <= math.exp(- delta_cost / T )):
				cur_sol = new_sol

		T *= r

	f = open("verify.in", "w")

	print("best_sol = " + str(best_sol))
	f.write(str(best_sol))
	f.write("\n")
	for request in best_requests: 
		f.write(f"{request.S_exe} {request.S_deliver} {request.T_wait} {request.catch_time}")
		print(f"{request.S_exe} {request.S_deliver} {request.T_wait} {request.catch_time}")
		#print(f"{request.S_deliver} ")
		#print(f"{request.T_wait} ")
		#print(f"{request.catch_time} ")
		f.write("\n")
	print("count: " + str(count))
	#get a initial solution
	sys.exit()
