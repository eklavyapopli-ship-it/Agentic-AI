// DOM Elements
const newTaskInput = document.getElementById('new-task-input');
const addTaskButton = document.getElementById('add-task-button');
const taskList = document.getElementById('task-list');
const filterButtons = document.querySelectorAll('.filter-button');
const startNowButton = document.getElementById('start-now');

let tasks = [];
let currentFilter = 'all';

// Function to load tasks from localStorage
function loadTasks() {
    const storedTasks = localStorage.getItem('tasks');
    if (storedTasks) {
        tasks = JSON.parse(storedTasks);
        renderTasks();
    }
}

// Function to save tasks to localStorage
function saveTasks() {
    localStorage.setItem('tasks', JSON.stringify(tasks));
}

// Function to create a task element
function createTaskElement(task) {
    const li = document.createElement('li');
    li.innerHTML = `
        <span class="task-text ${task.completed ? 'completed' : ''}">${task.text}</span>
        <button class="complete-button">${task.completed ? 'Undo' : 'Complete'}</button>
        <button class="delete-button">Delete</button>
    `;
    li.dataset.id = task.id;

    const completeButton = li.querySelector('.complete-button');
    const deleteButton = li.querySelector('.delete-button');

    completeButton.addEventListener('click', () => toggleComplete(task.id));
    deleteButton.addEventListener('click', () => deleteTask(task.id));

    return li;
}

// Function to render tasks based on the current filter
function renderTasks() {
    taskList.innerHTML = '';
    const filteredTasks = tasks.filter(task => {
        if (currentFilter === 'all') return true;
        if (currentFilter === 'completed') return task.completed;
        if (currentFilter === 'pending') return !task.completed;
        return false;
    });

    filteredTasks.forEach(task => {
        const taskElement = createTaskElement(task);
        taskList.appendChild(taskElement);
    });
}

// Function to add a new task
function addTask() {
    const taskText = newTaskInput.value.trim();
    if (taskText !== '') {
        const newTask = {
            id: Date.now(),
            text: taskText,
            completed: false
        };
        tasks.push(newTask);
        saveTasks();
        renderTasks();
        newTaskInput.value = '';
    }
}

// Function to toggle the completion status of a task
function toggleComplete(taskId) {
    tasks = tasks.map(task => {
        if (task.id === taskId) {
            task.completed = !task.completed;
        }
        return task;
    });
    saveTasks();
    renderTasks();
}

// Function to delete a task
function deleteTask(taskId) {
    tasks = tasks.filter(task => task.id !== taskId);
    saveTasks();
    renderTasks();
}

// Function to handle filter button clicks
function handleFilterClick(filter) {
    currentFilter = filter;
    filterButtons.forEach(button => button.classList.remove('active'));
    document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
    renderTasks();
}

// Event Listeners
addTaskButton.addEventListener('click', addTask);
newTaskInput.addEventListener('keypress', event => {
    if (event.key === 'Enter') {
        addTask();
    }
});

filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        handleFilterClick(button.dataset.filter);
    });
});

startNowButton.addEventListener('click', () => {
    document.getElementById('main').scrollIntoView({ behavior: 'smooth' });
});

// Initial Load
loadTasks();