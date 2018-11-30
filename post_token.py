import requests,json
from pandas import DataFrame
'''
post request to get token
store token into var token
'''
UP=0
DOWN=1
LEFT=2
RIGHT=3
dir_str=["UP","DOWN","LEFT","RIGHT"]
dir=[UP,DOWN,LEFT,RIGHT]
dir_r=["DOWN","UP","RIGHT","LEFT"]
dir_d=[[0,-1],[0,1],[-1,0],[1,0]]
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
def get_token():
	API="http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/session"
	body={"uid":"204917652"}
	r = requests.post(API, data=body,headers=headers)
	content=r.text
	json_acceptable= content.replace("'", "\"")
	content_dict=json.loads(json_acceptable)
	token=content_dict["token"]
	return content_dict
	print(token)


'''
use token to get current state
store current state to their corresponding variables 
'''
def get_current_state(token):
	url_get="http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game"
	#params_token={"token":token}
	r = requests.get(url_get, params=token)
	content=r.text
	json_acceptable= content.replace("'", "\"")
	content_dict=json.loads(json_acceptable)
	# maze_size=content_dict["maze_size"]
	# current_location=content_dict["current_location"]
	# status=content_dict["status"]
	# level_cp=content_dict["levels_completed"]
	# tot_level=content_dict["total_levels"]
	return content_dict

'''
post request to make a move
'''
def make_a_move(d,token):
	url_move="http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game"
	move={"action":d}
	r = requests.post(url_move, data=move,params=token, headers=headers)
	content=r.text
	json_acceptable= content.replace("'", "\"")
	content_dict=json.loads(json_acceptable)
	return content_dict
def out_of_bound(current_state,direction):
	x = current_state["current_location"][0]
	y = current_state["current_location"][1]
	if direction==UP:
		y-=1
	elif direction==DOWN:
		y+=1
	elif direction==LEFT:
		x-=1
	elif direction==RIGHT:
		x+=1
	num_x=current_state["maze_size"][0]
	num_y=current_state["maze_size"][1]
	if x<0 or x>=num_x:
		return True
	if y<0 or y>=num_y:
		return True
	return False
def hitWall(direction,token):
	re=make_a_move(direction,token)
	print(re["result"])
	return re["result"]=="WALL"
def construct_visited(current_state):
	x=current_state["maze_size"][0]
	y=current_state["maze_size"][1]
	visited=[[" " for j in range(x)] for i in range(y)]
	return visited
def should_move(q_x,q_y,cur_x,cur_y):
	print("moving")
	if q_x-cur_x==1:
		print("RIGHT")
		return RIGHT

	if q_x-cur_x==-1:
		print("LEFT")
		return LEFT
	if q_y-cur_y==1:
		print("DOWN")
		return DOWN
	if q_y-cur_y==-1:
		print("UP")
		return UP
#def dfs_start(start):
def dfs(current_state,token):
	print(current_state)
	x = current_state["current_location"][0]
	y = current_state["current_location"][1]
	print(x)
	print(y)
	for d in range(4):
		print(d)
		next_x=x+dir_d[d][0]
		next_y=y+dir_d[d][1]
		print(next_x)
		print(next_y)
		print(out_of_bound(current_state,dir[d]))
		out=False
		if next_x<0 or next_x>=current_state["maze_size"][0]:
			out=True
		if next_y<0 or next_y>=current_state["maze_size"][1]:
			out=True
		print(out)
		# print(next_x)
		# print(next_y)
		# print(visited[next_x][next_y])
		if (not out and visited[next_y][next_x] != "W" and visited[next_y][next_x]!="*"):

			print("NEXT")
			move = make_a_move(dir_str[d],token)
			print(move)
			if move["result"]=="OUT_OF_BOUNDS":
				print("asdas")
			if move["result"]=="END":
				# print("e")
				visited[next_y][next_x]="E"
				print(DataFrame(visited))
				return True
			elif move["result"]=="WALL":
				# print("w")
				visited[next_y][next_x]="W"

			elif move["result"]=="SUCCESS":

				print(DataFrame(visited))
				# print("asfsaaaaaaa")
				visited[next_y][next_x]="*"
				current_state=get_current_state(token)
				print(current_state)
				if dfs(current_state,token):
					# print("lol")
					return True
				else:
					print("aaa")
					make_a_move(dir_r[d],token)

token=get_token()
current_state=get_current_state(token)
visited =construct_visited(current_state)
print(DataFrame(visited))
# print(visited)
dfs(current_state,token)
print(get_current_state(token))







