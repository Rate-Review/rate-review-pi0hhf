import { rest, graphql } from 'msw';
import { HttpResponse } from 'msw';
import { 
  mockUsers,
  mockOrganizations,
  mockAttorneys,
  mockRates,
  mockNegotiations,
  mockMessages,
  mockAnalytics,
  mockOCGs,
  mockStaffClasses,
  mockPeerGroups,
  mockAIRecommendations
} from './data';
import { 
  AUTH_ROUTES,
  USER_ROUTES,
  ORGANIZATION_ROUTES,
  ATTORNEY_ROUTES,
  RATE_ROUTES,
  NEGOTIATION_ROUTES,
  MESSAGE_ROUTES,
  ANALYTICS_ROUTES,
  OCG_ROUTES,
  INTEGRATION_ROUTES,
  AI_ROUTES
} from '../../api/apiRoutes';

/**
 * Creates mock handlers for authentication-related API endpoints
 */
function createAuthHandlers() {
  return [
    rest.post(AUTH_ROUTES.LOGIN, async ({ request }) => {
      const { email, password } = await request.json();
      
      // Combine all users for lookup
      const allUsers = [
        ...mockUsers.lawFirmUsers,
        ...mockUsers.clientUsers,
        ...mockUsers.adminUsers
      ];
      
      const user = allUsers.find(u => u.email === email);
      
      if (!user || password !== 'password') {
        return new HttpResponse(
          JSON.stringify({ error: 'Invalid credentials' }),
          { status: 401 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({
          token: 'mock-jwt-token',
          refreshToken: 'mock-refresh-token',
          user
        }),
        { status: 200 }
      );
    }),
    
    rest.post(AUTH_ROUTES.LOGOUT, () => {
      return new HttpResponse(
        JSON.stringify({ success: true }),
        { status: 200 }
      );
    }),
    
    rest.get(AUTH_ROUTES.ME, () => {
      // Return admin user by default for simplicity
      return new HttpResponse(
        JSON.stringify({ user: mockUsers.adminUsers[0] }),
        { status: 200 }
      );
    }),
    
    rest.post(AUTH_ROUTES.REFRESH_TOKEN, () => {
      return new HttpResponse(
        JSON.stringify({
          token: 'new-mock-jwt-token',
          refreshToken: 'new-mock-refresh-token'
        }),
        { status: 200 }
      );
    }),
    
    rest.post(AUTH_ROUTES.RESET_PASSWORD, async () => {
      return new HttpResponse(
        JSON.stringify({ success: true }),
        { status: 200 }
      );
    }),
    
    rest.post(AUTH_ROUTES.VERIFY_EMAIL, async () => {
      return new HttpResponse(
        JSON.stringify({ success: true }),
        { status: 200 }
      );
    }),
    
    rest.post(AUTH_ROUTES.SETUP_MFA, async () => {
      return new HttpResponse(
        JSON.stringify({
          qrCodeUrl: 'https://example.com/qr-code',
          secretKey: 'mock-secret-key',
          success: true
        }),
        { status: 200 }
      );
    }),
    
    rest.post(AUTH_ROUTES.VERIFY_MFA, async ({ request }) => {
      const { code } = await request.json();
      
      if (code !== '123456') {
        return new HttpResponse(
          JSON.stringify({ error: 'Invalid MFA code' }),
          { status: 400 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ success: true }),
        { status: 200 }
      );
    })
  ];
}

/**
 * Creates mock handlers for user management API endpoints
 */
function createUserHandlers() {
  return [
    rest.get(USER_ROUTES.BASE, ({ request }) => {
      const url = new URL(request.url);
      const organizationId = url.searchParams.get('organizationId');
      const role = url.searchParams.get('role');
      
      let users = [
        ...mockUsers.lawFirmUsers,
        ...mockUsers.clientUsers,
        ...mockUsers.adminUsers
      ];
      
      if (organizationId) {
        users = users.filter(user => user.organizationId === organizationId);
      }
      
      if (role) {
        users = users.filter(user => user.role === role);
      }
      
      return new HttpResponse(
        JSON.stringify({
          items: users,
          total: users.length,
          page: 1,
          pageSize: 20,
          totalPages: 1
        }),
        { status: 200 }
      );
    }),
    
    rest.get(USER_ROUTES.BY_ID, ({ params }) => {
      const { id } = params;
      
      const allUsers = [
        ...mockUsers.lawFirmUsers,
        ...mockUsers.clientUsers,
        ...mockUsers.adminUsers
      ];
      
      const user = allUsers.find(u => u.id === id);
      
      if (!user) {
        return new HttpResponse(
          JSON.stringify({ error: 'User not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ user }),
        { status: 200 }
      );
    }),
    
    rest.post(USER_ROUTES.BASE, async ({ request }) => {
      const userData = await request.json();
      
      const newUser = {
        id: `user-${Date.now()}`,
        ...userData,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ user: newUser }),
        { status: 201 }
      );
    }),
    
    rest.put(USER_ROUTES.BY_ID, async ({ request, params }) => {
      const { id } = params;
      const userData = await request.json();
      
      const allUsers = [
        ...mockUsers.lawFirmUsers,
        ...mockUsers.clientUsers,
        ...mockUsers.adminUsers
      ];
      
      const userIndex = allUsers.findIndex(u => u.id === id);
      
      if (userIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'User not found' }),
          { status: 404 }
        );
      }
      
      const updatedUser = {
        ...allUsers[userIndex],
        ...userData,
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ user: updatedUser }),
        { status: 200 }
      );
    }),
    
    rest.delete(USER_ROUTES.BY_ID, () => {
      return new HttpResponse(
        JSON.stringify({ success: true }),
        { status: 200 }
      );
    }),
    
    rest.get(USER_ROUTES.PERMISSIONS, ({ params }) => {
      const { id } = params;
      
      const allUsers = [
        ...mockUsers.lawFirmUsers,
        ...mockUsers.clientUsers,
        ...mockUsers.adminUsers
      ];
      
      const user = allUsers.find(u => u.id === id);
      
      if (!user) {
        return new HttpResponse(
          JSON.stringify({ error: 'User not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ permissions: user.permissions }),
        { status: 200 }
      );
    })
  ];
}

/**
 * Creates mock handlers for organization-related API endpoints
 */
function createOrganizationHandlers() {
  return [
    rest.get(ORGANIZATION_ROUTES.BASE, ({ request }) => {
      const url = new URL(request.url);
      const type = url.searchParams.get('type');
      
      let organizations = [
        ...mockOrganizations.lawFirms,
        ...mockOrganizations.clients
      ];
      
      if (type) {
        organizations = organizations.filter(org => org.type === type);
      }
      
      return new HttpResponse(
        JSON.stringify({
          items: organizations,
          total: organizations.length,
          page: 1,
          pageSize: 20,
          totalPages: 1
        }),
        { status: 200 }
      );
    }),
    
    rest.get(ORGANIZATION_ROUTES.BY_ID, ({ params }) => {
      const { id } = params;
      
      const allOrganizations = [
        ...mockOrganizations.lawFirms,
        ...mockOrganizations.clients
      ];
      
      const organization = allOrganizations.find(org => org.id === id);
      
      if (!organization) {
        return new HttpResponse(
          JSON.stringify({ error: 'Organization not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ organization }),
        { status: 200 }
      );
    }),
    
    rest.post(ORGANIZATION_ROUTES.BASE, async ({ request }) => {
      const orgData = await request.json();
      
      const newOrg = {
        id: `org-${Date.now()}`,
        ...orgData,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ organization: newOrg }),
        { status: 201 }
      );
    }),
    
    rest.put(ORGANIZATION_ROUTES.BY_ID, async ({ request, params }) => {
      const { id } = params;
      const orgData = await request.json();
      
      const allOrganizations = [
        ...mockOrganizations.lawFirms,
        ...mockOrganizations.clients
      ];
      
      const orgIndex = allOrganizations.findIndex(org => org.id === id);
      
      if (orgIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Organization not found' }),
          { status: 404 }
        );
      }
      
      const updatedOrg = {
        ...allOrganizations[orgIndex],
        ...orgData,
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ organization: updatedOrg }),
        { status: 200 }
      );
    }),
    
    rest.get(ORGANIZATION_ROUTES.USERS, ({ params }) => {
      const { id } = params;
      
      let users = [
        ...mockUsers.lawFirmUsers,
        ...mockUsers.clientUsers,
        ...mockUsers.adminUsers
      ];
      
      users = users.filter(user => user.organizationId === id);
      
      return new HttpResponse(
        JSON.stringify({
          items: users,
          total: users.length,
          page: 1,
          pageSize: 20,
          totalPages: 1
        }),
        { status: 200 }
      );
    }),
    
    rest.get(ORGANIZATION_ROUTES.SETTINGS, ({ params }) => {
      const { id } = params;
      
      const allOrganizations = [
        ...mockOrganizations.lawFirms,
        ...mockOrganizations.clients
      ];
      
      const organization = allOrganizations.find(org => org.id === id);
      
      if (!organization) {
        return new HttpResponse(
          JSON.stringify({ error: 'Organization not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ settings: organization.settings }),
        { status: 200 }
      );
    }),
    
    rest.put(ORGANIZATION_ROUTES.SETTINGS, async ({ request }) => {
      const settingsData = await request.json();
      
      return new HttpResponse(
        JSON.stringify({
          success: true,
          settings: settingsData
        }),
        { status: 200 }
      );
    })
  ];
}

/**
 * Creates mock handlers for attorney and staff class API endpoints
 */
function createAttorneyHandlers() {
  return [
    rest.get(ATTORNEY_ROUTES.BASE, ({ request }) => {
      const url = new URL(request.url);
      const organizationId = url.searchParams.get('organizationId');
      const staffClassId = url.searchParams.get('staffClassId');
      const name = url.searchParams.get('name');
      
      let attorneys = [...mockAttorneys];
      
      if (organizationId) {
        attorneys = attorneys.filter(attorney => attorney.organizationId === organizationId);
      }
      
      if (staffClassId) {
        attorneys = attorneys.filter(attorney => attorney.staffClassId === staffClassId);
      }
      
      if (name) {
        attorneys = attorneys.filter(attorney => 
          attorney.name.toLowerCase().includes(name.toLowerCase())
        );
      }
      
      return new HttpResponse(
        JSON.stringify({
          items: attorneys,
          total: attorneys.length,
          page: 1,
          pageSize: 20,
          totalPages: 1
        }),
        { status: 200 }
      );
    }),
    
    rest.get(ATTORNEY_ROUTES.BY_ID, ({ params }) => {
      const { id } = params;
      
      const attorney = mockAttorneys.find(a => a.id === id);
      
      if (!attorney) {
        return new HttpResponse(
          JSON.stringify({ error: 'Attorney not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ attorney }),
        { status: 200 }
      );
    }),
    
    rest.post(ATTORNEY_ROUTES.BASE, async ({ request }) => {
      const attorneyData = await request.json();
      
      const newAttorney = {
        id: `attorney-${Date.now()}`,
        ...attorneyData,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ attorney: newAttorney }),
        { status: 201 }
      );
    }),
    
    rest.put(ATTORNEY_ROUTES.BY_ID, async ({ request, params }) => {
      const { id } = params;
      const attorneyData = await request.json();
      
      const attorneyIndex = mockAttorneys.findIndex(a => a.id === id);
      
      if (attorneyIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Attorney not found' }),
          { status: 404 }
        );
      }
      
      const updatedAttorney = {
        ...mockAttorneys[attorneyIndex],
        ...attorneyData,
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ attorney: updatedAttorney }),
        { status: 200 }
      );
    }),
    
    rest.get(ATTORNEY_ROUTES.PERFORMANCE, ({ params }) => {
      const { id } = params;
      
      const attorney = mockAttorneys.find(a => a.id === id);
      
      if (!attorney) {
        return new HttpResponse(
          JSON.stringify({ error: 'Attorney not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ 
          performance: mockAnalytics.attorneyPerformance 
        }),
        { status: 200 }
      );
    }),
    
    // Staff Classes
    rest.get('/staff-classes', ({ request }) => {
      const url = new URL(request.url);
      const organizationId = url.searchParams.get('organizationId');
      
      let staffClasses = [...mockStaffClasses];
      
      if (organizationId) {
        staffClasses = staffClasses.filter(sc => sc.organizationId === organizationId);
      }
      
      return new HttpResponse(
        JSON.stringify({
          items: staffClasses,
          total: staffClasses.length,
          page: 1,
          pageSize: 20,
          totalPages: 1
        }),
        { status: 200 }
      );
    }),
    
    rest.get('/staff-classes/:id', ({ params }) => {
      const { id } = params;
      
      const staffClass = mockStaffClasses.find(sc => sc.id === id);
      
      if (!staffClass) {
        return new HttpResponse(
          JSON.stringify({ error: 'Staff class not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ staffClass }),
        { status: 200 }
      );
    }),
    
    rest.post('/staff-classes', async ({ request }) => {
      const staffClassData = await request.json();
      
      const newStaffClass = {
        id: `staffclass-${Date.now()}`,
        ...staffClassData
      };
      
      return new HttpResponse(
        JSON.stringify({ staffClass: newStaffClass }),
        { status: 201 }
      );
    })
  ];
}

/**
 * Creates mock handlers for rate-related API endpoints
 */
function createRateHandlers() {
  return [
    rest.get(RATE_ROUTES.BASE, ({ request }) => {
      const url = new URL(request.url);
      const attorneyId = url.searchParams.get('attorneyId');
      const clientId = url.searchParams.get('clientId');
      const firmId = url.searchParams.get('firmId');
      const status = url.searchParams.get('status');
      const type = url.searchParams.get('type');
      
      // Combine all rates from mock data
      let rates = [
        ...mockRates.currentRates,
        ...mockRates.historicalRates,
        ...mockRates.proposedRates,
        ...mockRates.counterProposedRates
      ];
      
      // Apply filters
      if (attorneyId) {
        rates = rates.filter(rate => rate.attorneyId === attorneyId);
      }
      
      if (clientId) {
        rates = rates.filter(rate => rate.clientId === clientId);
      }
      
      if (firmId) {
        rates = rates.filter(rate => rate.firmId === firmId);
      }
      
      if (status) {
        rates = rates.filter(rate => rate.status === status);
      }
      
      if (type) {
        rates = rates.filter(rate => rate.type === type);
      }
      
      return new HttpResponse(
        JSON.stringify({
          items: rates,
          total: rates.length,
          page: 1,
          pageSize: 20,
          totalPages: 1
        }),
        { status: 200 }
      );
    }),
    
    rest.get(RATE_ROUTES.BY_ID, ({ params }) => {
      const { id } = params;
      
      // Combine all rates from mock data
      const allRates = [
        ...mockRates.currentRates,
        ...mockRates.historicalRates,
        ...mockRates.proposedRates,
        ...mockRates.counterProposedRates
      ];
      
      const rate = allRates.find(r => r.id === id);
      
      if (!rate) {
        return new HttpResponse(
          JSON.stringify({ error: 'Rate not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ rate }),
        { status: 200 }
      );
    }),
    
    rest.post(RATE_ROUTES.BASE, async ({ request }) => {
      const rateData = await request.json();
      
      const newRate = {
        id: `rate-${Date.now()}`,
        ...rateData,
        history: [
          {
            amount: rateData.amount,
            type: rateData.type,
            status: rateData.status,
            timestamp: new Date().toISOString(),
            userId: 'user-001',
            message: 'Rate created'
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ rate: newRate }),
        { status: 201 }
      );
    }),
    
    rest.put(RATE_ROUTES.BY_ID, async ({ request, params }) => {
      const { id } = params;
      const rateData = await request.json();
      
      // Combine all rates from mock data
      const allRates = [
        ...mockRates.currentRates,
        ...mockRates.historicalRates,
        ...mockRates.proposedRates,
        ...mockRates.counterProposedRates
      ];
      
      const rateIndex = allRates.findIndex(r => r.id === id);
      
      if (rateIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Rate not found' }),
          { status: 404 }
        );
      }
      
      const existingRate = allRates[rateIndex];
      
      const historyEntry = {
        amount: rateData.amount || existingRate.amount,
        type: rateData.type || existingRate.type,
        status: rateData.status || existingRate.status,
        timestamp: new Date().toISOString(),
        userId: 'user-001',
        message: rateData.message || 'Rate updated'
      };
      
      const updatedRate = {
        ...existingRate,
        ...rateData,
        history: [...existingRate.history, historyEntry],
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ rate: updatedRate }),
        { status: 200 }
      );
    }),
    
    rest.get(RATE_ROUTES.HISTORY, ({ params }) => {
      const { id } = params;
      
      // Combine all rates from mock data
      const allRates = [
        ...mockRates.currentRates,
        ...mockRates.historicalRates,
        ...mockRates.proposedRates,
        ...mockRates.counterProposedRates
      ];
      
      const rate = allRates.find(r => r.id === id);
      
      if (!rate) {
        return new HttpResponse(
          JSON.stringify({ error: 'Rate not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ history: rate.history }),
        { status: 200 }
      );
    }),
    
    rest.post(RATE_ROUTES.APPROVE, async ({ request, params }) => {
      const { id } = params;
      const { message } = await request.json();
      
      // Combine all rates from mock data
      const allRates = [
        ...mockRates.currentRates,
        ...mockRates.historicalRates,
        ...mockRates.proposedRates,
        ...mockRates.counterProposedRates
      ];
      
      const rateIndex = allRates.findIndex(r => r.id === id);
      
      if (rateIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Rate not found' }),
          { status: 404 }
        );
      }
      
      const existingRate = allRates[rateIndex];
      
      const historyEntry = {
        amount: existingRate.amount,
        type: 'APPROVED',
        status: 'APPROVED',
        timestamp: new Date().toISOString(),
        userId: 'user-001',
        message: message || 'Rate approved'
      };
      
      const updatedRate = {
        ...existingRate,
        type: 'APPROVED',
        status: 'APPROVED',
        history: [...existingRate.history, historyEntry],
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ rate: updatedRate }),
        { status: 200 }
      );
    }),
    
    rest.post(RATE_ROUTES.REJECT, async ({ request, params }) => {
      const { id } = params;
      const { message } = await request.json();
      
      // Combine all rates from mock data
      const allRates = [
        ...mockRates.currentRates,
        ...mockRates.historicalRates,
        ...mockRates.proposedRates,
        ...mockRates.counterProposedRates
      ];
      
      const rateIndex = allRates.findIndex(r => r.id === id);
      
      if (rateIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Rate not found' }),
          { status: 404 }
        );
      }
      
      const existingRate = allRates[rateIndex];
      
      const historyEntry = {
        amount: existingRate.amount,
        type: existingRate.type,
        status: 'REJECTED',
        timestamp: new Date().toISOString(),
        userId: 'user-001',
        message: message || 'Rate rejected'
      };
      
      const updatedRate = {
        ...existingRate,
        status: 'REJECTED',
        history: [...existingRate.history, historyEntry],
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ rate: updatedRate }),
        { status: 200 }
      );
    }),
    
    rest.post(RATE_ROUTES.COUNTER, async ({ request, params }) => {
      const { id } = params;
      const { amount, message } = await request.json();
      
      // Combine all rates from mock data
      const allRates = [
        ...mockRates.currentRates,
        ...mockRates.historicalRates,
        ...mockRates.proposedRates,
        ...mockRates.counterProposedRates
      ];
      
      const rateIndex = allRates.findIndex(r => r.id === id);
      
      if (rateIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Rate not found' }),
          { status: 404 }
        );
      }
      
      const existingRate = allRates[rateIndex];
      
      const historyEntry = {
        amount: amount,
        type: 'COUNTER_PROPOSED',
        status: 'UNDER_REVIEW',
        timestamp: new Date().toISOString(),
        userId: 'user-001',
        message: message || 'Rate counter-proposed'
      };
      
      const updatedRate = {
        ...existingRate,
        amount: amount,
        type: 'COUNTER_PROPOSED',
        status: 'UNDER_REVIEW',
        history: [...existingRate.history, historyEntry],
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ rate: updatedRate }),
        { status: 200 }
      );
    }),
    
    rest.post(RATE_ROUTES.IMPORT, async () => {
      return new HttpResponse(
        JSON.stringify({
          success: true,
          importedCount: 25,
          errors: [],
          importId: `import-${Date.now()}`
        }),
        { status: 200 }
      );
    }),
    
    rest.post(RATE_ROUTES.EXPORT, async () => {
      return new HttpResponse(
        JSON.stringify({
          success: true,
          exportedCount: 15,
          downloadUrl: 'https://example.com/exports/rates.xlsx',
          exportId: `export-${Date.now()}`
        }),
        { status: 200 }
      );
    })
  ];
}

/**
 * Creates mock handlers for negotiation-related API endpoints
 */
function createNegotiationHandlers() {
  return [
    rest.get(NEGOTIATION_ROUTES.BASE, ({ request }) => {
      const url = new URL(request.url);
      const status = url.searchParams.get('status');
      const clientId = url.searchParams.get('clientId');
      const firmId = url.searchParams.get('firmId');
      
      // Combine all negotiations from mock data
      let negotiations = [
        ...mockNegotiations.active,
        ...mockNegotiations.completed,
        ...mockNegotiations.requested
      ];
      
      // Apply filters
      if (status) {
        negotiations = negotiations.filter(n => n.status === status);
      }
      
      if (clientId) {
        negotiations = negotiations.filter(n => n.clientId === clientId);
      }
      
      if (firmId) {
        negotiations = negotiations.filter(n => n.firmId === firmId);
      }
      
      return new HttpResponse(
        JSON.stringify({
          items: negotiations,
          total: negotiations.length,
          page: 1,
          pageSize: 20,
          totalPages: 1
        }),
        { status: 200 }
      );
    }),
    
    rest.get(NEGOTIATION_ROUTES.BY_ID, ({ params }) => {
      const { id } = params;
      
      // Combine all negotiations from mock data
      const allNegotiations = [
        ...mockNegotiations.active,
        ...mockNegotiations.completed,
        ...mockNegotiations.requested
      ];
      
      const negotiation = allNegotiations.find(n => n.id === id);
      
      if (!negotiation) {
        return new HttpResponse(
          JSON.stringify({ error: 'Negotiation not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ negotiation }),
        { status: 200 }
      );
    }),
    
    rest.post(NEGOTIATION_ROUTES.BASE, async ({ request }) => {
      const negotiationData = await request.json();
      
      const newNegotiation = {
        id: `negotiation-${Date.now()}`,
        ...negotiationData,
        status: 'REQUESTED',
        messageThreadId: `thread-${Date.now()}`,
        rateIds: [],
        approvalWorkflowId: '',
        approvalStatus: 'PENDING',
        createdBy: 'user-001',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ negotiation: newNegotiation }),
        { status: 201 }
      );
    }),
    
    rest.put(NEGOTIATION_ROUTES.STATUS, async ({ request, params }) => {
      const { id } = params;
      const { status } = await request.json();
      
      // Combine all negotiations from mock data
      const allNegotiations = [
        ...mockNegotiations.active,
        ...mockNegotiations.completed,
        ...mockNegotiations.requested
      ];
      
      const negotiationIndex = allNegotiations.findIndex(n => n.id === id);
      
      if (negotiationIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Negotiation not found' }),
          { status: 404 }
        );
      }
      
      const existingNegotiation = allNegotiations[negotiationIndex];
      
      const updatedNegotiation = {
        ...existingNegotiation,
        status: status,
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ negotiation: updatedNegotiation }),
        { status: 200 }
      );
    }),
    
    rest.get(NEGOTIATION_ROUTES.RATES, ({ params }) => {
      const { id } = params;
      
      // Combine all negotiations from mock data
      const allNegotiations = [
        ...mockNegotiations.active,
        ...mockNegotiations.completed,
        ...mockNegotiations.requested
      ];
      
      const negotiation = allNegotiations.find(n => n.id === id);
      
      if (!negotiation) {
        return new HttpResponse(
          JSON.stringify({ error: 'Negotiation not found' }),
          { status: 404 }
        );
      }
      
      // Combine all rates from mock data
      const allRates = [
        ...mockRates.currentRates,
        ...mockRates.historicalRates,
        ...mockRates.proposedRates,
        ...mockRates.counterProposedRates
      ];
      
      // Filter rates that belong to this negotiation
      const negotiationRates = allRates.filter(r => 
        negotiation.rateIds.includes(r.id)
      );
      
      return new HttpResponse(
        JSON.stringify({ 
          rates: negotiationRates,
          total: negotiationRates.length 
        }),
        { status: 200 }
      );
    }),
    
    rest.post(NEGOTIATION_ROUTES.SUBMIT, async ({ request, params }) => {
      const { id } = params;
      const { rates } = await request.json();
      
      // Combine all negotiations from mock data
      const allNegotiations = [
        ...mockNegotiations.active,
        ...mockNegotiations.completed,
        ...mockNegotiations.requested
      ];
      
      const negotiationIndex = allNegotiations.findIndex(n => n.id === id);
      
      if (negotiationIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Negotiation not found' }),
          { status: 404 }
        );
      }
      
      const existingNegotiation = allNegotiations[negotiationIndex];
      
      // Create rate IDs for submitted rates
      const rateIds = rates.map((_, index) => `submitted-rate-${Date.now()}-${index}`);
      
      const updatedNegotiation = {
        ...existingNegotiation,
        status: 'SUBMITTED',
        rateIds: rateIds,
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({
          negotiation: updatedNegotiation,
          submittedRateIds: rateIds
        }),
        { status: 200 }
      );
    }),
    
    rest.post(NEGOTIATION_ROUTES.APPROVE, async ({ params }) => {
      const { id } = params;
      
      // Combine all negotiations from mock data
      const allNegotiations = [
        ...mockNegotiations.active,
        ...mockNegotiations.completed,
        ...mockNegotiations.requested
      ];
      
      const negotiationIndex = allNegotiations.findIndex(n => n.id === id);
      
      if (negotiationIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Negotiation not found' }),
          { status: 404 }
        );
      }
      
      const existingNegotiation = allNegotiations[negotiationIndex];
      
      const updatedNegotiation = {
        ...existingNegotiation,
        status: 'APPROVED',
        approvalStatus: 'APPROVED',
        completionDate: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ negotiation: updatedNegotiation }),
        { status: 200 }
      );
    }),
    
    rest.post(NEGOTIATION_ROUTES.REJECT, async ({ params }) => {
      const { id } = params;
      
      // Combine all negotiations from mock data
      const allNegotiations = [
        ...mockNegotiations.active,
        ...mockNegotiations.completed,
        ...mockNegotiations.requested
      ];
      
      const negotiationIndex = allNegotiations.findIndex(n => n.id === id);
      
      if (negotiationIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'Negotiation not found' }),
          { status: 404 }
        );
      }
      
      const existingNegotiation = allNegotiations[negotiationIndex];
      
      const updatedNegotiation = {
        ...existingNegotiation,
        status: 'REJECTED',
        approvalStatus: 'REJECTED',
        completionDate: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ negotiation: updatedNegotiation }),
        { status: 200 }
      );
    })
  ];
}

/**
 * Creates mock handlers for messaging and notification API endpoints
 */
function createMessageHandlers() {
  return [
    rest.get(MESSAGE_ROUTES.BASE, ({ request }) => {
      const url = new URL(request.url);
      const threadId = url.searchParams.get('threadId');
      
      let messages = [...mockMessages.messages];
      
      if (threadId) {
        messages = messages.filter(m => m.threadId === threadId);
      }
      
      return new HttpResponse(
        JSON.stringify({
          items: messages,
          total: messages.length,
          page: 1,
          pageSize: 20,
          totalPages: 1
        }),
        { status: 200 }
      );
    }),
    
    rest.get(MESSAGE_ROUTES.BY_ID, ({ params }) => {
      const { id } = params;
      
      const message = mockMessages.messages.find(m => m.id === id);
      
      if (!message) {
        return new HttpResponse(
          JSON.stringify({ error: 'Message not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ message }),
        { status: 200 }
      );
    }),
    
    rest.post(MESSAGE_ROUTES.BASE, async ({ request }) => {
      const messageData = await request.json();
      
      const newMessage = {
        id: `message-${Date.now()}`,
        ...messageData,
        sender: mockUsers.adminUsers[0], // For simplicity
        isRead: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ message: newMessage }),
        { status: 201 }
      );
    }),
    
    rest.get(MESSAGE_ROUTES.THREAD, ({ params }) => {
      const { id } = params;
      
      const thread = mockMessages.threads.find(t => t.id === id);
      
      if (!thread) {
        return new HttpResponse(
          JSON.stringify({ error: 'Thread not found' }),
          { status: 404 }
        );
      }
      
      // Get messages for this thread
      const threadMessages = mockMessages.messages.filter(
        m => m.threadId === id
      );
      
      return new HttpResponse(
        JSON.stringify({ 
          thread: thread,
          messages: threadMessages 
        }),
        { status: 200 }
      );
    }),
    
    rest.post(MESSAGE_ROUTES.THREAD, async ({ request }) => {
      const threadData = await request.json();
      
      const newThread = {
        id: `thread-${Date.now()}`,
        ...threadData,
        messageCount: 0,
        unreadCount: 0,
        latestMessage: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return new HttpResponse(
        JSON.stringify({ thread: newThread }),
        { status: 201 }
      );
    })
  ];
}

/**
 * Creates mock handlers for analytics API endpoints
 */
function createAnalyticsHandlers() {
  return [
    rest.get(ANALYTICS_ROUTES.IMPACT, () => {
      return new HttpResponse(
        JSON.stringify({ 
          impactAnalysis: mockAnalytics.rateImpact 
        }),
        { status: 200 }
      );
    }),
    
    rest.get(ANALYTICS_ROUTES.COMPARISON, () => {
      return new HttpResponse(
        JSON.stringify({ 
          peerComparison: mockAnalytics.peerComparison 
        }),
        { status: 200 }
      );
    }),
    
    rest.get(ANALYTICS_ROUTES.TRENDS, () => {
      return new HttpResponse(
        JSON.stringify({ 
          historicalTrends: mockAnalytics.historicalTrends 
        }),
        { status: 200 }
      );
    }),
    
    rest.get(ANALYTICS_ROUTES.PERFORMANCE, ({ request }) => {
      const url = new URL(request.url);
      const attorneyId = url.searchParams.get('attorneyId');
      
      if (!attorneyId) {
        return new HttpResponse(
          JSON.stringify({ error: 'Attorney ID is required' }),
          { status: 400 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ 
          performance: mockAnalytics.attorneyPerformance 
        }),
        { status: 200 }
      );
    }),
    
    rest.get(ANALYTICS_ROUTES.REPORTS, () => {
      return new HttpResponse(
        JSON.stringify({ 
          items: [],
          total: 0,
          page: 1,
          pageSize: 20,
          totalPages: 0
        }),
        { status: 200 }
      );
    }),
    
    rest.post(ANALYTICS_ROUTES.REPORTS, async ({ request }) => {
      const reportData = await request.json();
      
      const newReport = {
        id: `report-${Date.now()}`,
        ...reportData,
        status: 'COMPLETED',
        createdAt: new Date().toISOString(),
        createdBy: 'user-001',
        lastModified: new Date().toISOString(),
        data: [],
        chartData: []
      };
      
      return new HttpResponse(
        JSON.stringify({ report: newReport }),
        { status: 201 }
      );
    })
  ];
}

/**
 * Creates mock handlers for Outside Counsel Guidelines (OCG) API endpoints
 */
function createOCGHandlers() {
  return [
    rest.get(OCG_ROUTES.BASE, ({ request }) => {
      const url = new URL(request.url);
      const clientId = url.searchParams.get('clientId');
      
      let ocgs = [...mockOCGs];
      
      if (clientId) {
        ocgs = ocgs.filter(ocg => ocg.clientId === clientId);
      }
      
      return new HttpResponse(
        JSON.stringify({
          items: ocgs,
          total: ocgs.length,
          page: 1,
          pageSize: 20,
          totalPages: 1
        }),
        { status: 200 }
      );
    }),
    
    rest.get(OCG_ROUTES.BY_ID, ({ params }) => {
      const { id } = params;
      
      const ocg = mockOCGs.find(o => o.id === id);
      
      if (!ocg) {
        return new HttpResponse(
          JSON.stringify({ error: 'OCG not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ ocg }),
        { status: 200 }
      );
    }),
    
    rest.post(OCG_ROUTES.BASE, async ({ request }) => {
      const ocgData = await request.json();
      
      const newOCG = {
        id: `ocg-${Date.now()}`,
        ...ocgData,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      return new HttpResponse(
        JSON.stringify({ ocg: newOCG }),
        { status: 201 }
      );
    }),
    
    rest.put(OCG_ROUTES.BY_ID, async ({ request, params }) => {
      const { id } = params;
      const ocgData = await request.json();
      
      const ocgIndex = mockOCGs.findIndex(o => o.id === id);
      
      if (ocgIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'OCG not found' }),
          { status: 404 }
        );
      }
      
      const existingOCG = mockOCGs[ocgIndex];
      
      const updatedOCG = {
        ...existingOCG,
        ...ocgData,
        updatedAt: new Date()
      };
      
      return new HttpResponse(
        JSON.stringify({ ocg: updatedOCG }),
        { status: 200 }
      );
    }),
    
    rest.get(OCG_ROUTES.SECTIONS, ({ params }) => {
      const { id } = params;
      
      const ocg = mockOCGs.find(o => o.id === id);
      
      if (!ocg) {
        return new HttpResponse(
          JSON.stringify({ error: 'OCG not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ sections: ocg.sections }),
        { status: 200 }
      );
    }),
    
    rest.post(OCG_ROUTES.SECTIONS, async ({ request, params }) => {
      const { id } = params;
      const sectionData = await request.json();
      
      const ocgIndex = mockOCGs.findIndex(o => o.id === id);
      
      if (ocgIndex === -1) {
        return new HttpResponse(
          JSON.stringify({ error: 'OCG not found' }),
          { status: 404 }
        );
      }
      
      const newSection = {
        id: `section-${Date.now()}`,
        ...sectionData
      };
      
      return new HttpResponse(
        JSON.stringify({ section: newSection }),
        { status: 201 }
      );
    }),
    
    rest.get(OCG_ROUTES.ALTERNATIVES, ({ params }) => {
      const { id, sectionId } = params;
      
      const ocg = mockOCGs.find(o => o.id === id);
      
      if (!ocg) {
        return new HttpResponse(
          JSON.stringify({ error: 'OCG not found' }),
          { status: 404 }
        );
      }
      
      const section = ocg.sections.find(s => s.id === sectionId);
      
      if (!section) {
        return new HttpResponse(
          JSON.stringify({ error: 'Section not found' }),
          { status: 404 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ alternatives: section.alternatives }),
        { status: 200 }
      );
    }),
    
    rest.post(OCG_ROUTES.SELECTIONS, async ({ request }) => {
      const { selections } = await request.json();
      
      return new HttpResponse(
        JSON.stringify({ 
          success: true,
          selections: selections
        }),
        { status: 200 }
      );
    })
  ];
}

/**
 * Creates mock handlers for integration API endpoints
 */
function createIntegrationHandlers() {
  return [
    // eBilling Integration
    rest.post(INTEGRATION_ROUTES.EBILLING.TEST, async ({ request }) => {
      const connectionData = await request.json();
      
      // Simulate success for most requests, but fail for specific invalid data
      if (connectionData.baseUrl?.includes('invalid')) {
        return new HttpResponse(
          JSON.stringify({ 
            success: false,
            message: 'Unable to connect to the eBilling system'
          }),
          { status: 400 }
        );
      }
      
      return new HttpResponse(
        JSON.stringify({ 
          success: true,
          message: 'Connection successful'
        }),
        { status: 200 }
      );
    }),
    
    rest.post(INTEGRATION_ROUTES.EBILLING.IMPORT, async () => {
      return new HttpResponse(
        JSON.stringify({ 
          success: true,
          importId: `import-${Date.now()}`,
          recordsProcessed: 1250,
          recordsImported: 1240,
          errors: []
        }),
        { status: 200 }
      );
    }),
    
    rest.post(INTEGRATION_ROUTES.EBILLING.EXPORT, async () => {
      return new HttpResponse(
        JSON.stringify({ 
          success: true,
          exportId: `export-${Date.now()}`,
          recordsExported: 45,
          errors: []
        }),
        { status: 200 }
      );
    }),
    
    // UniCourt Integration
    rest.get(INTEGRATION_ROUTES.UNICOURT.SEARCH, ({ request }) => {
      const url = new URL(request.url);
      const query = url.searchParams.get('q');
      
      if (!query) {
        return new HttpResponse(
          JSON.stringify({ 
            results: [] 
          }),
          { status: 200 }
        );
      }
      
      // Simulate a basic search result
      return new HttpResponse(
        JSON.stringify({ 
          results: mockAttorneys.slice(0, 3).map(a => ({
            id: a.unicourtId,
            name: a.name,
            barDate: a.barDate,
            courts: ['SDNY', 'EDNY', 'DNJ'],
            caseCount: Math.floor(Math.random() * 100) + 20
          }))
        }),
        { status: 200 }
      );
    }),
    
    rest.get(INTEGRATION_ROUTES.UNICOURT.ATTORNEY, ({ params }) => {
      const { id } = params;
      
      // Find a matching attorney by unicourtId
      const attorney = mockAttorneys.find(a => a.unicourtId === id);
      
      if (!attorney) {
        return new HttpResponse(
          JSON.stringify({ error: 'Attorney not found in UniCourt' }),
          { status: 404 }
        );
      }
      
      // Return mock UniCourt data for this attorney
      return new HttpResponse(
        JSON.stringify({ 
          unicourtAttorney: {
            id: attorney.unicourtId,
            name: attorney.name,
            barDate: attorney.barDate,
            courts: ['SDNY', 'EDNY', 'DNJ'],
            caseCount: attorney.performanceData.unicourt.caseCount,
            winRate: attorney.performanceData.unicourt.winRate,
            caseTypes: attorney.performanceData.unicourt.caseTypes,
            percentile: attorney.performanceData.unicourt.percentile
          }
        }),
        { status: 200 }
      );
    }),
    
    // File Import/Export
    rest.post(INTEGRATION_ROUTES.FILE.IMPORT, async () => {
      return new HttpResponse(
        JSON.stringify({ 
          success: true,
          importId: `file-import-${Date.now()}`,
          recordsProcessed: 150,
          recordsImported: 148,
          errors: []
        }),
        { status: 200 }
      );
    }),
    
    rest.post(INTEGRATION_ROUTES.FILE.EXPORT, async () => {
      return new HttpResponse(
        JSON.stringify({ 
          success: true,
          exportId: `file-export-${Date.now()}`,
          downloadUrl: 'https://example.com/exports/data.xlsx',
          recordsExported: 75
        }),
        { status: 200 }
      );
    })
  ];
}

/**
 * Creates mock handlers for AI-related API endpoints
 */
function createAIHandlers() {
  return [
    rest.post(AI_ROUTES.CHAT, async ({ request }) => {
      const { message } = await request.json();
      
      // Find a mock response based on the message, or return a default
      const mockResponse = mockAIRecommendations.chatResponses.find(
        cr => cr.query.toLowerCase().includes(message.toLowerCase())
      ) || {
        query: message,
        response: 'I understand your question. Let me analyze the data and get back to you with insights about this topic.',
        contentType: 'text'
      };
      
      return new HttpResponse(
        JSON.stringify({ 
          response: mockResponse.response,
          contentType: mockResponse.contentType,
          conversationId: 'conv-123'
        }),
        { status: 200 }
      );
    }),
    
    rest.post(AI_ROUTES.RECOMMENDATIONS.RATES, async ({ request }) => {
      const { rateIds } = await request.json();
      
      let recommendations = [];
      
      if (rateIds && rateIds.length > 0) {
        // Filter to include only the requested rate IDs
        recommendations = mockAIRecommendations.rateRecommendations.filter(
          rec => rateIds.includes(rec.rateId)
        );
      } else {
        // Return all recommendations if no specific IDs were requested
        recommendations = mockAIRecommendations.rateRecommendations;
      }
      
      return new HttpResponse(
        JSON.stringify({ recommendations }),
        { status: 200 }
      );
    }),
    
    rest.post(AI_ROUTES.RECOMMENDATIONS.ACTIONS, async () => {
      return new HttpResponse(
        JSON.stringify({ 
          recommendations: [
            {
              id: 'action-rec-001',
              action: 'review_negotiation',
              entityId: 'negotiation-001',
              entityType: 'NEGOTIATION',
              priority: 'HIGH',
              title: 'Review counter-proposals from Acme Corporation',
              description: 'Acme Corporation has counter-proposed rates for 1 of your attorneys. Review and respond to keep the negotiation moving forward.',
              dueDate: '2023-10-25T23:59:59Z',
              confidence: 0.92
            },
            {
              id: 'action-rec-002',
              action: 'submit_rates',
              entityId: 'negotiation-003',
              entityType: 'NEGOTIATION',
              priority: 'MEDIUM',
              title: 'Submit rates for Tech Innovations',
              description: 'Tech Innovations requested rate submission by December 15, 2023. Prepare and submit your rates to avoid delays.',
              dueDate: '2023-12-01T23:59:59Z',
              confidence: 0.85
            },
            {
              id: 'action-rec-003',
              action: 'review_analytics',
              entityId: 'analytics-impact',
              entityType: 'ANALYTICS',
              priority: 'LOW',
              title: 'Review rate impact analysis',
              description: 'Analyze the financial impact of recent rate changes to better understand their effect on your budget.',
              dueDate: null,
              confidence: 0.78
            }
          ]
        }),
        { status: 200 }
      );
    }),
    
    rest.post(AI_ROUTES.ANALYZE, async () => {
      return new HttpResponse(
        JSON.stringify({ 
          analysis: 'Based on the provided data, I can see that the proposed rates represent a 4.1% increase over current rates, which is slightly above the peer group average of 3.9%. The highest increases are from ABC Law (4.2%) and XYZ Legal (4.1%), while Smith & Jones has the lowest at 3.2%. This is within the peer range of 3.0-4.8%, but you might want to consider negotiating the highest increases to bring them closer to the average.',
          insights: [
            'Proposed rates are 0.2% above peer group average',
            'ABC Law has the highest increase at 4.2%',
            'All proposed increases are within client guidelines',
            'Projected annual impact is $102,500'
          ]
        }),
        { status: 200 }
      );
    }),
    
    rest.get(AI_ROUTES.CONFIGURATION, () => {
      return new HttpResponse(
        JSON.stringify({ 
          aiProvider: 'JUSTICE_BID',
          modelName: 'gpt-4',
          userPersonalization: true,
          dataAccess: {
            rateData: true,
            negotiationData: true,
            attorneyPerformance: true,
            historicalData: true
          },
          maxTokens: 4096,
          temperature: 0.2
        }),
        { status: 200 }
      );
    }),
    
    rest.put(AI_ROUTES.CONFIGURATION, async ({ request }) => {
      const configData = await request.json();
      
      return new HttpResponse(
        JSON.stringify({ 
          success: true,
          configuration: configData
        }),
        { status: 200 }
      );
    })
  ];
}

// Combine all handlers
const handlers = [
  ...createAuthHandlers(),
  ...createUserHandlers(),
  ...createOrganizationHandlers(),
  ...createAttorneyHandlers(),
  ...createRateHandlers(),
  ...createNegotiationHandlers(),
  ...createMessageHandlers(),
  ...createAnalyticsHandlers(),
  ...createOCGHandlers(),
  ...createIntegrationHandlers(),
  ...createAIHandlers()
];

export default handlers;