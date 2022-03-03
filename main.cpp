#include <map>
#include <iostream>
#include <fstream>
#include <vector>

using namespace std;


vector<string> split (string s, string delimiter) {
    size_t pos_start = 0, pos_end, delim_len = delimiter.length();
    string token;
    vector<string> res;

    while ((pos_end = s.find (delimiter, pos_start)) != string::npos) {
        token = s.substr (pos_start, pos_end - pos_start);
        pos_start = pos_end + delim_len;
        res.push_back (token);
    }

    res.push_back (s.substr (pos_start));
    return res;
}

int compile(vector<string> instructs){
	map<string, int> memory;
	vector<string> instructions = instructs;
    int instruct_pointer = 0;
    while (true) {
    	if(instruct_pointer >= (int) instructions.size()){
    		break;
    	}
    	vector<string> disassemble = split(instructions[instruct_pointer], " ");
    	if(disassemble[0] == "mov"){
    		if (memory.count(disassemble[2]) == 0) {
    			memory[disassemble[1]] = stoi(disassemble[2]);
			} else {
				memory[disassemble[1]] = memory.find(disassemble[2])->second;
			}}
		if(disassemble[0] == "inc"){
			if (memory.count(disassemble[1]) != 0){
				memory.find(disassemble[1])->second++;
			}}
		if(disassemble[0] == "dec"){
			if (memory.count(disassemble[1]) != 0){
				memory.find(disassemble[1])->second--;
			}}
		if(disassemble[0] == "jnz"){
			if (memory.count(disassemble[1]) != 0){
				if (memory.find(disassemble[1])->second != 0)
				{
				    instruct_pointer += stoi(disassemble[2]);
				    continue;
				}
			}else{
				if (stoi(disassemble[1]) != 0)
				{
				    instruct_pointer += stoi(disassemble[2]);
				    continue;
				}
			}}
		if(disassemble[0] == "del"){
			if (memory.count(disassemble[1]) != 0){memory.erase(disassemble[1]);}
		}


    	instruct_pointer += 1;
    }
    for (auto const& x : memory)
	{
	    std::cout << x.first  // string (key)
	              << ':' 
	              << x.second // string's value 
	              << std::endl;
	}
    cin.get();
    return 0;
}

int main () {
	string line;
	ifstream myfile ("main.asm");
	vector<string> instructs;
	if (myfile.is_open())
	{
		while (getline(myfile,line))
		{
			instructs.push_back(line);
		}
		myfile.close();
	}

	else cout << "Unable to open file"; 


	compile(instructs);
}
