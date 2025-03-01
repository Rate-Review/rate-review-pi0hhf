import { setupServer } from 'msw'; // msw ^1.2.1
import { rest } from 'msw'; // msw ^1.2.1
import { axiosInstance } from '../../../api/axiosConfig';
import { handleApiError } from '../../../api/errorHandling';
import { render } from '../../testUtils';
import { requestInterceptor, responseInterceptor } from '../../../api/interceptors';
import api from '../../../services/api';
import MockAdapter from 'axios-mock-adapter'; // axios-mock-adapter ^1.21.4
import axios from 'axios'; // axios ^1.4.0

describe('API Service', () => {
  const mockServer = setupServer();

  beforeAll(() => {
    mockServer.listen();
  });

  afterAll(() => {
    mockServer.close();
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    mockServer.resetHandlers();
  });

  test('should make a successful GET request', async () => {
    const mockData = { message: 'Hello, world!' };
    mockServer.use(
      rest.get('/test', (req, res, ctx) => {
        return res(ctx.status(200), ctx.json(mockData));
      })
    );

    const data = await api.get('/test');
    expect(data).toEqual(mockData);
  });

  test('should make a successful POST request', async () => {
    const mockData = { message: 'Data received!' };
    mockServer.use(
      rest.post('/test', (req, res, ctx) => {
        return res(ctx.status(201), ctx.json(mockData));
      })
    );

    const testData = { input: 'Test data' };
    const data = await api.post('/test', testData);
    expect(data).toEqual(mockData);
  });

  test('should make a successful PUT request', async () => {
    const mockData = { message: 'Data updated!' };
    mockServer.use(
      rest.put('/test', (req, res, ctx) => {
        return res(ctx.status(200), ctx.json(mockData));
      })
    );

    const testData = { input: 'Updated data' };
    const data = await api.put('/test', testData);
    expect(data).toEqual(mockData);
  });

  test('should make a successful DELETE request', async () => {
    const mockData = { message: 'Data deleted!' };
    mockServer.use(
      rest.delete('/test', (req, res, ctx) => {
        return res(ctx.status(200), ctx.json(mockData));
      })
    );

    const data = await api.delete('/test');
    expect(data).toEqual(mockData);
  });

  test('should handle API errors correctly', async () => {
    mockServer.use(
      rest.get('/error', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ message: 'Server error' }));
      })
    );

    await expect(api.get('/error')).rejects.toThrow('Server error');
  });

  test('should apply request interceptors', async () => {
    const mock = new MockAdapter(axiosInstance);
    const interceptorSpy = jest.spyOn(axiosInstance.interceptors.request, 'use');
    mockServer.use(
      rest.get('/intercepted', (req, res, ctx) => {
        return res(ctx.status(200), ctx.json({ message: 'Intercepted!' }));
      })
    );
    mock.onGet('/intercepted').reply(200, { message: 'Intercepted!' });

    await api.get('/intercepted');

    expect(interceptorSpy).toHaveBeenCalled();
  });

  test('should apply response interceptors', async () => {
    const mock = new MockAdapter(axiosInstance);
    const interceptorSpy = jest.spyOn(axiosInstance.interceptors.response, 'use');
    mockServer.use(
      rest.get('/responseIntercepted', (req, res, ctx) => {
        return res(ctx.status(200), ctx.json({ message: 'Response Intercepted!' }));
      })
    );
    mock.onGet('/responseIntercepted').reply(200, { message: 'Response Intercepted!' });

    await api.get('/responseIntercepted');

    expect(interceptorSpy).toHaveBeenCalled();
  });

  test('should retry failed requests based on configuration', async () => {
    let attempt = 0;
    mockServer.use(
      rest.get('/retry', (req, res, ctx) => {
        attempt++;
        if (attempt < 3) {
          return res(ctx.status(503));
        }
        return res(ctx.status(200), ctx.json({ message: 'Success after retry' }));
      })
    );

    const data = await api.get('/retry');
    expect(data).toEqual({ message: 'Success after retry' });
    expect(attempt).toBe(3);
  });
});