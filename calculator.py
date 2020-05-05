from collections import deque


class Calculator:

    def __init__(self):
        self.vars = {}
        self.help = "This calculator supports arithmetic operations " \
                    + "on integers: addition, subtraction, " \
                    + "multiplication, division and exponentiation. " \
                    + "It also supports variable assignment."
        self.operations = {
            '-': lambda left: left.__sub__,
            '+': lambda left: left.__add__,
            '*': lambda left: left.__mul__,
            '/': lambda left: left.__floordiv__,
            '^': lambda left: left.__pow__
        }
        self.precedence = {
            '-': 0,
            '+': 0,
            '*': 1,
            '/': 1,
            '^': 2
        }

    def has_precedence(self, incoming, top):
        return self.precedence[incoming] > self.precedence[top]

    def exec_command(self, command):
        stop = False
        if command == "exit":
            message, stop = "Bye!", True
        elif command == "help":
            message = self.help
        else:
            message = "Unknown command"
        return message, stop

    def assign(self, variable, value):
        if not variable.isalpha():
            return "Invalid identifier"
        elif value.isalpha():
            value = self.vars.get(value)
            if not value:
                return "Unknown variable"
        elif value.isnumeric():
            value = int(value)
        else:
            return "Invalid assignment"
        self.vars[variable] = value

    def choose_sign(self, sign_group):
        if len(sign_group) == 1:
            return sign_group
        minus_signs = [sign for sign in sign_group if sign == '-']
        return '-' if len(minus_signs) % 2 else '+'

    def sanitize(self, user_input):
        user_input = user_input.replace('(-', '(0-').replace('-(', '-1*(')
        if user_input[0] == '-':
            user_input = '0' + user_input
        items = deque(user_input)
        infix, digit_group, sign_group = [], '', ''
        while items:
            item = items.popleft()
            if item == '(':
                if sign_group:
                    sign = self.choose_sign(sign_group)
                    infix.append(sign)
                    sign_group = ''
                infix.append(item)
            elif item == ')':
                if digit_group:
                    infix.append(digit_group)
                    digit_group = ''
                infix.append(item)
            elif item in self.operations:
                if digit_group:
                    infix.append(digit_group)
                    digit_group = ''
                if item in '*/^' and sign_group:
                    return
                sign_group += item
            else:
                if sign_group:
                    sign = self.choose_sign(sign_group)
                    infix.append(sign)
                    sign_group = ''
                digit_group += item
        if sign_group:
            return
        elif digit_group:
            infix.append(digit_group)
        return infix

    def infix_to_postfix(self, infix):
        postfix = []
        stack = deque()
        for item in infix:
            if item in self.operations:
                if not stack or stack[-1] == '(':
                    stack.append(item)
                elif self.precedence[item] > self.precedence[stack[-1]]:
                    stack.append(item)
                else:
                    top = stack[-1]
                    while top:
                        if top == '(' or self.precedence[item] > self.precedence[top]:
                            break
                        postfix.append(stack.pop())
                        top = stack[-1] if stack else None
                    stack.append(item)
            elif item == '(':
                stack.append(item)
            elif item == ')':
                top = stack[-1] if stack else None
                while top:
                    if top == '(':
                        break
                    postfix.append(stack.pop())
                    if not stack:
                        return
                    top = stack[-1]
                stack.pop()
            else:
                postfix.append(item)
        if '(' in stack or ')' in stack:
            return
        while stack:
            postfix.append(stack.pop())
        return postfix

    def calculate_postfix(self, postfix):
        stack = deque()
        for item in postfix:
            if item not in self.operations:
                if item.isalpha():
                    try:
                        item = self.vars[item]
                    except KeyError:
                        return "Unknown variable"
                stack.append(int(item))
            elif len(stack) >= 2:
                right, left = stack.pop(), stack.pop()
                result = self.operations[item](left)(right)
                stack.append(result)
            else:
                return "Invalid expression"
        return stack.pop()

    def calculate_expression(self, expression):
        infix = self.sanitize(expression)
        if not infix:
            return "Invalid expression"
        postfix = self.infix_to_postfix(infix)
        if not postfix:
            return "Invalid expression"
        return self.calculate_postfix(postfix)


def main():
    calc = Calculator()

    while True:
        user_input = ''.join(input().split())
        if not user_input:
            continue
        elif user_input[0] == '/':
            message, stop = calc.exec_command(user_input[1:])
            print(message)
            if stop:
                break
        elif '=' in user_input:
            items = user_input.split('=')
            error = calc.assign(items[0], '='.join(items[1:]))
            if error:
                print(error)
        else:
            print(calc.calculate_expression(user_input))


if __name__ == "__main__":
    main()
