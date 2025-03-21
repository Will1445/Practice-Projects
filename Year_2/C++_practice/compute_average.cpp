#include <iostream>

int main(){
    int num1, num2, num3;

    std::cout << "Input your first number:";
    std::cin >> num1;

    std::cout << "Input your second number";
    std::cin >> num2;

    std::cout << "Input your third number";
    std::cin >> num3;

    double average = (num1 + num2 + num3) / 3.0;
    std::cout << "The average is: " << average << std::endl;

    return 0;
}
