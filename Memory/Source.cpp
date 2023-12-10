#include<iostream>
#include<vector>
#include<string>
#include<bitset>
#include <sstream>
#include<fstream>
#include <cmath>
#include<iomanip>
using namespace std;

const int mian_memory_access = 120;
string hexToBinary(const string& hexString) {
    string binaryString;
    string temp = "";
    

    for (char hexChar : hexString) {
        int value;
        stringstream ss;
        ss << hex << hexChar;
        ss >> value;
        binaryString += bitset<4>(value).to_string();
    }
    //for (int i = 0; i < totoal_length - binaryString.length(); i++)           //to Add zeros till reaching the desired length(if needed)
    //{
    //    temp += "0";
    //}
    //binaryString = temp + binaryString;
    return binaryString;
}


class Address {
public:
	string hex, tag, index, offset;

	Address(){
	}
    void Initialize(string original, string str, int index_size, int offset_size) {
        int tag_size = str.length() - index_size - offset_size;
        hex = original;
        tag = str.substr(0, tag_size);
        index = str.substr(tag_size, index_size);
        offset = str.substr(tag_size + index_size, offset_size);
    }
};


class CacheLine {

public:
    bool valid = 0;
    string tag; // String Temporarily untill choosing the right data type.'
    string data;
    string index;

    CacheLine() {
        valid = 0;
        tag = "";
        data = "";
    }
};


vector<Address> create_adderes( int index_size, int offset_size) {
    vector<Address> Adresses;
    //Read File

    ifstream inputFile("Addresses.txt");

    if (!inputFile.is_open()) {
        cerr << "Error opening the file!" << endl;
    }

    vector<string> data;
    Address A;

    string line;
    while (getline(inputFile, line)) {
        stringstream ss(line);
        string cell;
        string binary_addres;

        while (getline(ss, cell, ',')) {
            binary_addres = hexToBinary(cell.substr(2));
            A.Initialize(cell, binary_addres, index_size, offset_size);
            Adresses.push_back(A);

        }

    }    
    inputFile.close();



    return Adresses;
}


void display(int accesses, int hit, int miss,int hit_penality,int miss_penality, CacheLine Cache[], int cache_size, Address A) {
    cout << "Accessing  " << A.hex << endl;
    cout << setw(8) << "Index" << setw(8)<< "Tag" << " | " << setw(8) << "Data" << endl;
    for (int i = 0; i < cache_size; i++) {
        if (Cache[i].valid) {
            cout << setw(8) << Cache[i].index << setw(8) << Cache[i].tag << " | " << setw(8) << Cache[i].data << endl;
        }
    }
    cout << "Total Number of accesses: "<<accesses<<endl;
    double hits_ratio = (double(hit) / double(accesses)) ;
    cout << "Hits ratio: " << setprecision(2) << hits_ratio*100<<"%" << endl;
    cout << "Misses ratio: " << setprecision(2) << (1-hits_ratio) * 100 << "%" << endl;
    cout << "AMAT: " << int(hits_ratio * hit_penality + (1 - hits_ratio) * miss_penality) <<"cycles";

}

int main() {

    int hits=0, misses=0,accesses=0;
  
    int S, L, cache_access;
    int indx_size, disp_size;
    cout << "Enter S,L,Cache cycles:  ";
    cin >> S >> L >> cache_access;
    disp_size = log2(L);
    int C = S / L;
    indx_size = log2(C);

    int hit_penality = cache_access;
    int miss_penality = cache_access + mian_memory_access;

    vector<Address> Addresses = create_adderes(indx_size, disp_size);
    CacheLine* Cache = new CacheLine[C];
    int n;

    for (int i = 0; i < Addresses.size(); i++) {
        n = stoi(Addresses[i].index, nullptr, 2);
        if (Cache[n].valid == 0) {
            Cache[n].tag = Addresses[i].tag;        //I could Have stored the content in the cache as well but it is written that it is irrelevant.
            Cache[n].data = Addresses[i].offset;
            Cache[n].index= Addresses[i].index;
            Cache[n].valid = 1;
            misses++;
        }
        else {
            if (Cache[n].tag == Addresses[i].tag)   //hit
            {
                hits++;
            }
            else {          //miss
                Cache[n].tag = Addresses[i].tag;
                Cache[n].data =  Addresses[i].offset;
                Cache[n].index = Addresses[i].index;
                misses++;
            }
        }
        accesses++;
        display(accesses,hits,misses,hit_penality,miss_penality, Cache, C, Addresses[i]);
    }


    


}