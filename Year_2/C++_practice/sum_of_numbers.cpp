#include <iostream>

int main(){
    int num;

    std::cout << "Enter an integer: ";
    std::cin >> num;

    int total = 0;
    for (int i = 1; i <= num; i++){
        total = total + i;
    }

    std::cout << "Sum of natural numbers up to " << num << " is " << total << std::endl;

    return 0;
}