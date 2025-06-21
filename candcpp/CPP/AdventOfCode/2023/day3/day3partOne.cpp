#include <stdio.h>
#include <iostream>
#include <vector>
#include <string>
#include <fstream>

bool isContained(std::string t, char a){
    for(int i = 0; i < t.length(); i++){
        if(t.at(i) == a){return true;}
    }
    return false;
}

template <class T>
void printArr(std::vector<T>* arr){
    if(arr->size() == 0){ std::cout << "{}" << std::endl; return;}
    if(arr->size() == 1){ std::cout << "{" << arr->at(0) << "}" << std::endl; return;}
    std::cout << "{" << arr->at(0) << ",";
    for(int i = 1; i < arr->size() - 1; i++){
        std::cout << arr->at(i) << ",";
    }
    std::cout << arr->at(arr->size()-1) << "}";
}

std::vector<std::vector<char>>* convertToArray (std::string fileName){
    std::vector<std::vector<char>>* array = new std::vector<std::vector<char>>;

    std::ifstream file;
    file.open(fileName);
    std::string line;
    
    int j = 0;
    while(getline(file, line)){
        std::vector<char> newLine;
        array->push_back(newLine);
        for(int i = 0; i < line.length(); i++){
            array->at(j).push_back(line.at(i)); 
        }
        j++;
    }
    file.close();

    return array;
}

bool checkNeighbours(std::vector<int>* y, std::vector<int>* x, std::vector<std::vector<char>>* array){
    for(int i = 0; i < x->size(); i++){
        for(int col = -1; col <= 1; col++){
            for(int row = -1; row <= 1; row++){
                if((y->at(i)+col != -1 && x->at(i)+row != -1) &&
                   (y->at(i)+col != array->size() && x->at(i)+row != array->at(i).size())){
                    if(!isContained("1234567890.", array->at(y->at(i)+col).at(x->at(i)+row))) return true;
                }
            }
        }
    }
    return false;
}

int sumNumbers(std::vector<std::vector<char>>* array){
    std::string numberString = "0123456789"; 
    int sum = 0;
    int j = 0;
    std::vector<int>* y = new std::vector<int>;
    std::vector<int>* x = new std::vector<int>;

    for(int j = 0; j < array->size(); j++){
        std::string numString = "";
        for(int i = 0; i < array->at(j).size(); i++){
            if(isContained(numberString, array->at(j).at(i))){
                numString += array->at(j).at(i);
                y->push_back(j);
                x->push_back(i);
            }
            else if(numString != ""){
                if(checkNeighbours(y, x, array)){
                    sum += std::stoi(numString);
                    std::cout << numString << ", " << y->at(0) << std::endl;
                }
                numString = "";
                y->clear();
                x->clear();
            }
        }
        /* Cuando se llega al eol, hay que "limpiar" */
        if(checkNeighbours(y, x, array)){
            sum += std::stoi(numString);
            std::cout << numString << ", " << y->at(0) << std::endl;
        }
        numString = "";
        y->clear();
        x->clear();
    }
    return sum;
}

int main(){
    std::vector<std::vector<char>>* array = convertToArray("input.txt");
    std::cout << sumNumbers(array) << std::endl;
    return 0;
}

