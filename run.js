#!/usr/bin/env node

const { spawn } = require('child_process');

// Get the arguments passed to the npm script, slicing off the first two
// which are the path to node and the path to this script.
const args = process.argv.slice(2);

// Spawn the Python script, passing along all arguments.
// 'stdio: inherit' connects the python script's input, output, and errors
// directly to the user's terminal, making it a seamless experience.
const pythonProcess = spawn('graphqlnomad', args, { stdio: 'inherit' });

// Handle errors, such as if the 'graphqlnomad' command isn't found.
pythonProcess.on('error', (err) => {
  console.error('Error: Failed to start the Python script.');
  console.error('Please ensure Python and pip are installed correctly and that "graphqlnomad" is available in your PATH.');
  console.error(err);
  process.exit(1);
});

// Exit the Node.js process with the same exit code as the Python script.
pythonProcess.on('exit', (code) => {
  process.exit(code);
});