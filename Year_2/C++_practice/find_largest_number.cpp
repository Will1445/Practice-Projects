#include <iostream>

int main(){
    int num1, num2, num3;

    std::cout << "Input your first number:";
    std::cin >> num1;

    std::cout << "Input your second number:";
    std::cin >> num2;

    std::cout << "Input your third number:";
    std::cin >> num3;

    if (num1 > num2 && num1 > num3){
        std::cout << num1 << " is the largest number" << std::endl;
    }

    else if (num2 > num1 && num2 > num3){
        std::cout << num2 << " is the largest number" << std::endl;
    }

    else if (num3 > num1 && num3 > num2){
        std::cout << num3 << " is the largest number" << std::endl;
    }

    else {
        std::cout << "Two of the numbers are the same!" << std::endl;
    }

    return 0;
}
