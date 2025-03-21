#include <iostream>

int main(){
    int num1, num2;

    std::cout << "Input your first number:";
    std::cin >> num1;

    std::cout << "Input your second number:";
    std::cin >> num2;

    int sum = num1 + num2;
    std::cout << "The sum is:" << sum << std::endl;

    return 0;
}