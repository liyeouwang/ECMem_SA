'''
#TODO: 
still not considering share type
consider freshness
ideal slot should have a map to their corresponding S_deliver, so that we don't need to spend time find their S_deliver
'''
import numpy as np
import math 
import sys
import copy
import time
import bisect

T_MAX = 0

class Slot:
	def __init__(self, start, end):
		self.start = start
		self.end = end
		self.duration = end - start 

		#for ideal slot
		self.S_deliver = -1

class Vehicle:
	def __init__(self, vehicle_id, num_servers): 
		self.vehicle_id = vehicle_id
		self.range = [0] * num_servers

		self.servers = []

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
		self.reassign_list = []
		self.slots = []

		self.vehicle_in = [0] * num_vehicles
		self.vehicle_out = [0] * num_vehicles
		self.loading = 0

		def evaluation_function(self):
			return self.loading
		def __lt__(self, other):
			return self.evaluation_function() < other.evaluation_function()

class Request:
	def __init__(self, vehicle_id, service_type, ID, num_servers):
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

		self.ideal_slots = [0] * num_servers
		self.earliest_start_time = 0 # = T_request

def decide_delivery_time():
	for request in requests:
		request.catch_time = min(request.deadline, T_MAX-1)
		for j in range(len(servers)):
			if(vehicles[request.vehicle_id].range[j][request.catch_time] == 1):
				request.S_deliver = j
				break

# TODO: need to consider deadline !! 
# and freshness 
def partition_ideal_range():
	for request in requests:
		for j in range(len(servers)):
			for jj in vehicles[request.vehicle_id].servers:
				T_deliver = services[request.service_type].T_deliver[j][jj]
				T_compute = services[request.service_type].T_compute[j]
				T_request = services[request.service_type].T_request[j]
				if(T_compute + T_deliver <= request.freshness):
					for i in range(len(servers[jj].vehicle_in[request.vehicle_id])):
						if(servers[jj].vehicle_in[request.vehicle_id][i] <= request.deadline):
							start = max(T_request, servers[jj].vehicle_in[request.vehicle_id][i] - T_deliver - T_compute)
							end = min(request.deadline - T_deliver, servers[jj].vehicle_out[request.vehicle_id][i] - T_deliver)
			
							if(end - start > services[request.service_type].T_compute[j]):
								request.ideal_slots[j].append(Slot(start, end))

	

def sort_requests():
	requests = sort(requests, key = lambda x: x.size, inverse = True) 

def fit(ideal_slot, request, server):
	is_scheduled = False
	T_compute = services[request.service_type].T_compute[server.server_id]

	for slot in server.slots:
		#print("request ID: " + str(request.ID) + " slot start: " + str(slot.start) + " end: " + str(slot.end))
		#case 1
		if(slot.start >= ideal_slot.start and slot.end <= ideal_slot.end):
			if(slot.end - slot.start >= T_compute):
				is_scheduled = True
				request.T_compute = T_compute
				request.start_exe_time = slot.end - request.T_compute
				new_slot = Slot(slot.start, request.start_exe_time)
				slot.start = request.start_exe_time + request.T_compute + 1
				if(new_slot.duration > 0):
					server.slots.insert(server.slots.index(slot)+1, new_slot)
				if(slot.duration <= 0):
					server.slots.remove(slot)
				break

		#case 3
		if(slot.start >= ideal_slot.start and slot.start <= ideal_slot.end and slot.end >= ideal_slot.end):
			if(ideal_slot.end - slot.start >= T_compute):
				is_scheduled = True
				request.T_compute = T_compute
				request.start_exe_time = slot.start
				slot.start = request.start_exe_time + request.T_compute + 1
				if(slot.duration <= 0):
					server.slots.remove(slot)
				break

		#case 4
		if(slot.start <= ideal_slot.start and slot.end >= ideal_slot.start and slot.end <= ideal_slot.end):
			if(slot.end - ideal_slot.start >= T_compute):
				is_scheduled = True
				request.T_compute = T_compute
				request.start_exe_time = slot.end - request.T_compute
				slot.end = request.start_exe_time
				if(slot.duration <= 0):
					server.slots.remove(slot)
				break

		if(slot.start <= ideal_slot.start and slot.end >= ideal_slot.end):
			is_scheduled = True
			request.T_compute = T_compute
			request.start_exe_time = ideal_slot.end - request.T_compute
			new_slot = Slot(slot.start, request.start_exe_time)
			slot.start = request.start_exe_time + request.T_compute + 1
			if(new_slot.duration > 0):
				server.slots.insert(server.slots.index(slot)+1, new_slot)
			if(slot.duration <= 0):
				server.slots.remove(slot)
			break

	return is_scheduled
def ideal_scheduling(request, possible_servers):
	for s in possible_servers:
		for ideal_slot in request.ideal_slots[s[0]]:
			if(fit(ideal_slot, request, servers[s[0]]) == True):
				request.S_exe = s[0]
				return True

		# find ideal slot in this server
		# update server loading
def non_ideal_scheduling(request, possible_servers):
	for s in possible_servers:
		if(find_slot(request, servers[s[0]]) == True):
			request.S_exe = s[0]
			return 
		# find slot
		# update server loading

	print("can't schedule")

def update_server_loading(possible_servers, request):
	possible_servers.remove((request.S_exe, servers[request.S_exe].loading))
	servers[request.S_exe].loading += request.T_compute
	possible_servers.append((request.S_exe, servers[request.S_exe].loading))
	possible_servers = sorted(possible_servers, key=lambda x: x[1])

def assign_to_servers():

	for server in servers:
		server.slots.clear()
		server.slots.append(Slot(0, T_MAX-1))
	possible_servers = []
	for s in range(len(servers)):
		possible_servers.append((s, servers[s].loading))

	for request in requests:
		if(ideal_scheduling(request, possible_servers) == True):	
			continue
		else:
			non_ideal_scheduling(request, possible_servers)

		update_server_loading(possible_servers, request)



def decide_exe_servers():

	sorted_requests = sorted(requests, key = lambda x: x.deadline) 
	

	j = 0
	for request in sorted_requests:
		request.S_exe = j
		request.T_compute = services[request.service_type].T_compute[j]
		request.T_deliver = services[request.service_type].T_deliver[j][request.S_deliver]
		servers[j].exe_queue.append(request.ID)
		#no consider freshness
		j+=1
		if(j >= len(servers)):
			j = 0

'''
slot: (start, end]
ex: slot.start=0  slot.end = 5
duration: 5
availabe time: 0, 1, 2, 3, 4 
'''
# need to fix: latest_start_time, earliest_start_time 
def find_slot(request, server):	
	is_scheduled = False

	if(request.T_compute + request.T_deliver > request.freshness):
		#server.reassign_list.append(request)
		#print("not scheduled (freshness): " + str(request.ID))	
		return False

	for slot in server.slots:
		if(slot.end - slot.start >= request.T_compute):
			if((request.latest_start_time < slot.start) or (request.earliest_start_time + request.T_compute >= slot.end)):
				#(request.earliest_start_time + request.T_compute > slot.end) maybe cant just break
				continue

			is_scheduled = True
			if(slot.end > request.latest_start_time + request.T_compute):
				request.start_exe_time = request.latest_start_time
			else:
				request.start_exe_time = slot.end - request.T_compute
			new_slot = Slot(slot.start, request.start_exe_time)
			slot.start = request.start_exe_time + request.T_compute + 1
			if(new_slot.duration > 0):
				server.slots.insert(server.slots.index(slot)+1, new_slot)
			if(slot.duration <= 0):
				server.slots.remove(slot)
			break
		#if(is_scheduled == False):
			#server.reassign_list.append(request)
			#print("not scheduled: " + str(request.ID))	
		#else:
			#print("scheduled: " + str(request.ID))	
			#queue.remove(request)

	return is_scheduled


def decide_exe_priority():

	'''
	for each server
		prioritize tasks in decreasing order based on their memory size (or should be T_compute? )
		for each prioritized task
			schedule it in the latest possible free slot that meets its deadline (latest start exe time)

			if can't schedule it:
				move it to another queue (may be reassigned to another server) 
	'''

	for request in requests:
		request.earliest_start_time = max(request.T_request, request.catch_time - request.freshness)
		request.latest_start_time = request.catch_time - request.T_deliver - request.T_compute

	for server in servers:

		queue = []
		for r in server.exe_queue:
			queue.append(requests[r])
		queue.sort(key=lambda x: x.size, reverse=True)
		#queue.sort(key=lambda x: x.T_compute, reverse=True)

		server.reassign_list.clear()
		server.slots.clear()
		server.slots.append(Slot(0, T_MAX-1))
		#find_slot(queue, server)
		for request in queue:
			if(find_slot(request, server) == False):
				server.reassign_list.append(request)

	#sys.exit()

def refresh(request, new_server):
	request.S_exe = new_server.server_id
	request.T_request = services[request.service_type].T_request[new_server.server_id]
	request.T_compute = services[request.service_type].T_compute[new_server.server_id]
	request.T_deliver = services[request.service_type].T_deliver[new_server.server_id][request.S_deliver]
	request.earliest_start_time = max(request.T_request, request.catch_time - request.freshness)
	request.latest_start_time = request.catch_time - request.T_deliver - request.T_compute

def balance_servers_load():

	for server in servers:
		is_scheduled_list = []
		print("server id: "+str(server.server_id) + " len of reassign_list " + str(len(server.reassign_list)))
		for request in server.reassign_list:
			print(request.ID)
			for new_server in servers:
				refresh(request, new_server)
				is_scheduled = find_slot(request, new_server)
				if(is_scheduled == True):
					is_scheduled_list.append(request)
					print("is_scheduled: " + str(request.ID))
					break
					#server.reassign_list.remove(request)
		
		print("server id: "+str(server.server_id) + " len of reassign_list " + str(len(server.reassign_list)))
		for scheduled_request in is_scheduled_list:
			print(scheduled_request.ID)
			server.reassign_list.remove(scheduled_request)

	for server in servers:
		print("len of reassign_list " + str(len(server.reassign_list)))

def find_better_deliver_servers():
	for request in requests:
		is_catch = False
		waiting_time_list = []
		for j in range(len(servers)):
			T_deliver = services[request.service_type].T_deliver[request.S_exe][j]
			finish_time = request.start_exe_time + request.T_compute + T_deliver
			index = bisect.bisect_left(servers[j].in_range[request.vehicle_id], finish_time)

			if(index >= len(servers[j].in_range[request.vehicle_id])):
				is_catch = False
				waiting_time = 1000000
			else:
				is_catch = True
				catch_time = servers[j].in_range[request.vehicle_id][index]
				if(catch_time > request.deadline):
					waiting_time = 1000000
				else:
					waiting_time = catch_time - finish_time
			waiting_time_list.append(waiting_time)

		request.S_deliver = waiting_time_list.index(min(waiting_time_list))
		request.T_deliver = services[request.service_type].T_deliver[request.S_exe][request.S_deliver]
		request.catch_time = request.start_exe_time + request.T_compute + request.T_deliver + waiting_time_list[request.S_deliver]

def accumulate_memory():
	#init
	for server in servers:
		server.memory = [0] * T_MAX
	all_max_memory_use = 0

	for request in requests:
		request.finish_time = request.start_exe_time + request.T_compute + request.T_deliver
		for t in range(request.finish_time, request.catch_time):

			servers[request.S_deliver].memory[t] += request.size

	for server in servers:
		max_memory_use = max(server.memory)
		all_max_memory_use += max_memory_use

	return all_max_memory_use

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
				requests.append(Request(i, k, num_requests, num_servers))
				num_requests += 1

	for r in range(len(requests)):
		for j in range(len(servers)):
			requests[r].ideal_slots[j] = []
	'''
	for k in range(num_services):
		print(services[k].deadline)
	'''

	for i in range(num_vehicles):
		freshnesses = [int(x) for x in input().split()]
		for k in range(num_services):
			services[k].freshness[i] = freshnesses[k]
			#print(freshnesses[k])
	

	for i in range(num_vehicles):
		for j in range(num_servers):
			vehicles[i].range[j] = [0] * T_MAX

	
	for j in range(num_servers):
		for i in range(num_vehicles):
			servers[j].in_range[i] = []
			servers[j].vehicle_in[i] = []
			servers[j].vehicle_out[i] = []

	for i in range(num_vehicles):
		for j in range(num_servers):
			ranges = [int(x) for x in input().split()]
			
			for t in range(T_MAX):
				vehicles[i].range[j][t] = ranges[t]
				if(ranges[t] == 1):
					servers[j].in_range[i].append(t)
					if(t == 0):
						servers[j].vehicle_in[i].append(t)
						vehicles[i].servers.append(j)
					elif(ranges[t-1] == 0):
						servers[j].vehicle_in[i].append(t)
						vehicles[i].servers.append(j)
					if(t == T_MAX-1):
						servers[j].vehicle_out[i].append(t)
					elif(ranges[t+1] == 0):
						servers[j].vehicle_out[i].append(t)
			if(len(servers[j].vehicle_out[i])!=len(servers[j].vehicle_in[i])):
				print("in out not equal")
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

if __name__ == '__main__':
	start_time = time.time()

	servers = []	
	services = []
	vehicles = []
	requests = []

	#read input file	
	read_inputs(services, servers, vehicles, requests)
	print(time.time() - start_time)

	init_requests(requests, services)
	print(time.time() - start_time)


	#decide_delivery_time()
	partition_ideal_range()
	print(time.time() - start_time)

	assign_to_servers()
	print(time.time() - start_time)

	find_better_deliver_servers()
	print(time.time() - start_time)

	#decide_exe_servers()
	#decide_exe_priority()
	#balance_servers_load()
	#find_better_deliver_servers()
	
	sol = accumulate_memory()
	print(time.time() - start_time)
	
	end_time = time.time()
	sys.exit()

	print(sol)
	for request in requests: 
		if(vehicles[request.vehicle_id].range[request.S_deliver][request.catch_time] != 1):
			print("no catch")
		print(f"{request.vehicle_id} {request.service_type} {request.S_exe} {request.S_deliver} {request.start_exe_time} {request.catch_time}")

