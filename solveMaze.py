import requests,json
from pandas import DataFrame
UP=0
DOWN=1
LEFT=2
RIGHT=3
dir_str=["UP","DOWN","LEFT","RIGHT"]
dir_r=["DOWN","UP","RIGHT","LEFT"]
dir_d=[[0,-1],[0,1],[-1,0],[1,0]]
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

#post request to get token
#store token into var token
def get_token():
	API="http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/session"
	body={"uid":"204917652"}
	r = requests.post(API, data=body,headers=headers)
	content=r.text
	json_acceptable= content.replace("'", "\"")
	content_dict=json.loads(json_acceptable)
	token=content_dict["token"]
	return content_dict

#use token to get current state
#store current state to their corresponding variables 
def get_current_state(token):
	url_get="http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game"
	r = requests.get(url_get, params=token)
	content=r.text
	json_acceptable= content.replace("'", "\"")
	content_dict=json.loads(json_acceptable)
	return content_dict

#post request to make a move
def make_a_move(d,token):
	url_move="http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game"
	move={"action":d}
	r = requests.post(url_move, data=move,params=token, headers=headers)
	content=r.text
	json_acceptable= content.replace("'", "\"")
	content_dict=json.loads(json_acceptable)
	return content_dict
def hitWall(direction,token):
	re=make_a_move(direction,token)
	return re["result"]=="WALL"
def construct_visited(current_state):
	x=current_state["maze_size"][0]
	y=current_state["maze_size"][1]
	visited=[[" " for j in range(x)] for i in range(y)]
	return visited
#major function to solve the maze
def dfs(current_state,token):
	x = current_state["current_location"][0]
	y = current_state["current_location"][1]
	for d in range(4):
		next_x=x+dir_d[d][0]
		next_y=y+dir_d[d][1]
		#check if out of bound
		out=False
		if next_x<0 or next_x>=current_state["maze_size"][0]:
			out=True
		if next_y<0 or next_y>=current_state["maze_size"][1]:
			out=True

		if (not out and visited[next_y][next_x] != "W" and visited[next_y][next_x]!="*"):
			move = make_a_move(dir_str[d],token)
			if move["result"]=="END":
				visited[next_y][next_x]="E"
				print(DataFrame(visited))
				return True
			elif move["result"]=="WALL":
				visited[next_y][next_x]="W"

			elif move["result"]=="SUCCESS":

				print(DataFrame(visited))
				visited[next_y][next_x]="*"
				current_state=get_current_state(token)
				if dfs(current_state,token):
					return True
				else:
					make_a_move(dir_r[d],token)

for i in range(5):
	token=get_token()
	current_state=get_current_state(token)
	visited =construct_visited(current_state)
	print(DataFrame(visited))
	dfs(current_state,token)
	print(get_current_state(token))









