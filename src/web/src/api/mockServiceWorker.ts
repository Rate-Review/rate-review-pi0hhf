// msw version: ^1.0.0
import { setupWorker } from 'msw'; // Import the setupWorker function from MSW
import { rest } from 'msw'; // Import the rest object from MSW
import handlers from '../tests/mocks/handlers'; // Import the request handlers

// Check if the code is running in a testing environment
if (process.env.NODE_ENV === 'development') {
  // Create a mock service worker with the defined handlers
  const worker = setupWorker(...handlers);

  // Define a function to start the worker
  const startWorker = () => {
    // Start the worker and log a message
    worker.start({
      onUnhandledRequest: 'bypass',
    });
    console.log('Mock service worker started');
  };

  // Define a function to stop the worker
  const stopWorker = () => {
    worker.close();
    console.log('Mock service worker stopped');
  };

  // Start the worker immediately
  startWorker();

  // Export the worker instance for use in tests and development
  export { worker };
}