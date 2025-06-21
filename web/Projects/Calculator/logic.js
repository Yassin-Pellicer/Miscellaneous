class Calculator{
    constructor(previousValueTextElement, currentValueTextElement){
        this.previousValueTextElement = previousValueTextElement;
        this.currentValueTextElement = currentValueTextElement;
        this.clear();
    }

    clear(){
        this.currentValue = '';
        this.previousValue = '';
        this.operation = undefined;
    }

    appendNumber(number){
        if(number === '.' && this.currentValue.toString().includes('.')){return;}
        this.currentValue = this.currentValue.toString() + number.toString();
    }

    appendOperation(operation){
        if(this.currentValue === ''){
            return;
        }
        if(this.previousValue !== ''){
            this.compute();
        }
        this.previousValue = this.currentValue;
        this.currentValue = '';
        this.operation = operation;
    }

    changeSign(){
        if(this.currentValue == ''){
            return;
        }
        this.currentValue = this.currentValue * -1;
    }

    compute(){
        let computation;
        let firstval = parseFloat(this.previousValue);
        let secondval = parseFloat(this.currentValue);

        if(isNaN(firstval) || isNaN(secondval)){
            return;
        }
        switch(this.operation){
            case '+':
                computation = firstval + secondval;
                break;
            case '-':
                computation = firstval - secondval;
                break;
            case '*':
                computation = firstval * secondval;
                break;
            case '÷':
                computation = firstval / secondval;
                break;
            default:
                return;
        }
        if(isNaN(computation) || !isFinite(computation)){
            return;
        }
        else{
            this.previousValue = '';
            computation = parseFloat(computation.toFixed(4));
            this.currentValue = computation;
            this.operation = undefined;
        }
    }

    delete(){
        this.currentValue = this.currentValue.toString().slice(0,-1);
    }

    updateDisplay(){
        if(this.currentValue.toString().length != 0){
            this.currentValueTextElement.innerText = this.currentValue;
        }
        else{
            this.currentValueTextElement.innerText = '--'
        }

        if(this.previousValue.toString().length != 0){
            this.previousValueTextElement.innerText = this.previousValue + ` ${this.operation}`;
        }
        else{
            this.previousValueTextElement.innerText = '--'
        }
    }
}

const previousValueTextElement = document.querySelector('[previous-value]');
const currentValueTextElement = document.querySelector('[current-value]');
const numberButtons = document.querySelectorAll('[number-button]');
const operationButtons = document.querySelectorAll('[operation-button]');
const deleteButton = document.querySelector('[delete-button]');
const clearAll = document.querySelector('[clear-button]');
const equalsButton = document.querySelector('[equals-button]');
const changeSignButton = document.querySelector('[change-sign-button]');

const calculator = new Calculator(previousValueTextElement, currentValueTextElement);

numberButtons.forEach(button => {
    button.addEventListener('click', () =>{
        calculator.appendNumber(button.innerText);
        calculator.updateDisplay();
    })
})

operationButtons.forEach(button => {
    button.addEventListener('click', () =>{
        calculator.appendOperation(button.innerText);
        calculator.updateDisplay();
    })
})

deleteButton.addEventListener('click', () =>{
    calculator.delete();
    calculator.updateDisplay();
})

clearAll.addEventListener('click', () =>{
    calculator.clear();
    calculator.updateDisplay();
})

clearAll.addEventListener('click', () =>{
    calculator.clear();
    calculator.updateDisplay();
})

equalsButton.addEventListener('click', () =>{
    calculator.compute();
    calculator.updateDisplay();
})

changeSignButton.addEventListener('click', () =>{
    calculator.changeSign();
    calculator.updateDisplay();
})