from app import app
from flask import render_template, request, make_response, redirect, url_for
from .linked_list import LinkedList
import json

# Helper function to determine if a character is an operator
def is_operator(char):
    return char in "+-*/^"  # Returns True or False

# Helper function to define operator precedence
def precedence(operator):
    if operator in "+-":
        return 1
    if operator in "*/":
        return 2
    if operator == "^":
        return 3
    return 0

# Helper function to validate the input expression
def is_valid_expression(expression):
    expression = expression.replace("–", "-")  # Replace en dash with hyphen-minus
    stack = []
    valid_chars = set("0123456789+-*/^()abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") # Set of valid characters in the input expression
    last_char = ""
    
    for char in expression.replace(" ", ""): # Ensures that the input expression has no spaces
        if char not in valid_chars:
            print(f"Invalid character found: {char}")
            return False  # Invalid character found
        if char == "(":
            stack.append(char)
        elif char == ")":
            if not stack or stack[-1] != "(":
                print("Unmatched closing parenthesis")
                return False  # Unmatched closing parenthesis
            stack.pop()
        elif is_operator(char):
            if not last_char or is_operator(last_char) or last_char == "(":
                print("Invalid operator placement")
                return False  # Invalid operator placement
        elif char.isalnum():  # Check if alphanumeric (digits or letters)
            if last_char and last_char.isalnum():
                continue  # Allow consecutive alphanumeric characters
        last_char = char

    # Ensure no unmatched opening parentheses and last character is valid
    if stack:
        print("Unmatched opening parenthesis")
    if not (last_char.isalnum() or last_char == ")"):
        print("Invalid last character")
    return not stack and (last_char.isalnum() or last_char == ")")

# Infix to Postfix conversion
def infix_to_postfix(expression):
    expression = expression.replace("–", "-")  # Replace en dash with hyphen-minus
    operator_stack = LinkedList()  # Stack to hold operators
    postfix = LinkedList()  # Linked list (treated as stack) to hold the postfix expression
    expression = expression.replace(" ", "")  # Removes spaces before transforming to postfix
    steps = []  # List to hold step-by-step details
    
    i = 0
    while i < len(expression):
        step_detail = {
            "expression": expression[:i+1],  # Include only the current character in the expression
            "stack": operator_stack.to_list(),
            "postfix": postfix.to_list()
        }
        
        if expression[i].isalnum():  # Checks if element is an operand (digit or letter)
            operand = expression[i]
            while i + 1 < len(expression) and expression[i + 1].isalnum():
                i += 1
                operand += expression[i]
            postfix.insert_at_end(operand)  # Push the full operand to the postfix stack

        elif expression[i] == '(':
            operator_stack.insert_at_beginning(expression[i])  # Push to operator stack
        elif expression[i] == ')':
            # If the top of the operator_stack is an opening bracket
            while operator_stack.head and operator_stack.head.data != '(':
                # Pop element from the operator_stack and push to the postfix stack
                postfix.insert_at_end(operator_stack.remove_beginning())
            operator_stack.remove_beginning()  # Pop the '(' from the stack
        elif is_operator(expression[i]):
            # While an operator at the top of the operators stack has greater/equal precedence than element
            while (operator_stack.head and precedence(operator_stack.head.data) >= precedence(expression[i])):
                # Pop operator from the operator_stack into the postfix stack
                postfix.insert_at_end(operator_stack.remove_beginning())
            operator_stack.insert_at_beginning(expression[i])  # Push element in the operator stack
        
        step_detail["stack"] = operator_stack.to_list()
        step_detail["postfix"] = postfix.to_list()
        steps.append(step_detail)
        i += 1

    # Pop remaining operators from the operator stack to the postfix stack
    while operator_stack.head:
        postfix.insert_at_end(operator_stack.remove_beginning())
        steps.append({
            "expression": expression,
            "stack": operator_stack.to_list(),
            "postfix": postfix.to_list()
        })
    
    return postfix.to_list(), steps  # Returns a list for readability and steps

@app.route('/infix-to-postfix', methods=['GET', 'POST'])
def Infix_to_Postfix():
    if request.method == 'POST':
        input_expr = request.form['input']
        if not is_valid_expression(input_expr):  # Validate input expression
            response = make_response(redirect(url_for('Infix_to_Postfix')))
            response.set_cookie('input_expr', input_expr)
            response.set_cookie('output', 'Invalid Expression! Try again...')
            return response

        output, steps = infix_to_postfix(input_expr)
        response = make_response(redirect(url_for('Infix_to_Postfix')))
        response.set_cookie('input_expr', input_expr)
        response.set_cookie('output', " ".join(output))
        response.set_cookie('steps', json.dumps(steps))
        return response
    
    input_expr = request.cookies.get('input_expr', '')
    output = request.cookies.get('output', '')
    steps = json.loads(request.cookies.get('steps', '[]'))
    response = make_response(render_template('infix_to_postfix.html', 
                                             title="Infix To Postfix",
                                             input=input_expr,
                                             output=output,
                                             steps=steps))
    response.set_cookie('input_expr', '', expires=0)
    response.set_cookie('output', '', expires=0)
    response.set_cookie('steps', '', expires=0)
    return response