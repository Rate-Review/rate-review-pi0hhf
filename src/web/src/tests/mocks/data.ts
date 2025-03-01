import { User } from '../../types/user';
import { Organization, PeerGroup } from '../../types/organization';
import { Attorney } from '../../types/attorney';
import { Rate, StaffClass } from '../../types/rate';
import { Negotiation } from '../../types/negotiation';
import { Message } from '../../types/message';
import { OCG } from '../../types/ocg';
import { AnalyticsData } from '../../types/analytics';

// Mock Organizations (Law Firms and Clients)
export const mockOrganizations = {
  lawFirms: [
    {
      id: 'firm-001',
      name: 'ABC Law LLP',
      type: 'LawFirm',
      domain: 'abclaw.com',
      settings: {
        rateRules: {},
        approvalWorkflow: {},
        afaTarget: 0,
        defaultCurrency: 'USD'
      },
      offices: [
        {
          id: 'office-001',
          name: 'New York',
          city: 'New York',
          state: 'NY',
          country: 'USA',
          region: 'Northeast'
        },
        {
          id: 'office-002',
          name: 'Los Angeles',
          city: 'Los Angeles',
          state: 'CA',
          country: 'USA',
          region: 'West'
        }
      ],
      departments: [
        {
          id: 'dept-001',
          name: 'Litigation',
          description: 'General litigation practice'
        },
        {
          id: 'dept-002',
          name: 'Corporate',
          description: 'Corporate and M&A practice'
        }
      ],
      contacts: [
        {
          id: 'contact-001',
          userId: 'user-001',
          name: 'John Smith',
          email: 'jsmith@abclaw.com',
          role: 'Billing Manager',
          phone: '212-555-1234',
          isActive: true,
          lastVerified: new Date('2023-09-01')
        }
      ],
      createdAt: new Date('2020-01-01'),
      updatedAt: new Date('2023-01-15')
    },
    {
      id: 'firm-002',
      name: 'XYZ Legal Group',
      type: 'LawFirm',
      domain: 'xyzlegal.com',
      settings: {
        rateRules: {},
        approvalWorkflow: {},
        afaTarget: 0,
        defaultCurrency: 'USD'
      },
      offices: [
        {
          id: 'office-003',
          name: 'Chicago',
          city: 'Chicago',
          state: 'IL',
          country: 'USA',
          region: 'Midwest'
        },
        {
          id: 'office-004',
          name: 'Washington DC',
          city: 'Washington',
          state: 'DC',
          country: 'USA',
          region: 'Northeast'
        }
      ],
      departments: [
        {
          id: 'dept-003',
          name: 'Intellectual Property',
          description: 'IP and patent practice'
        },
        {
          id: 'dept-004',
          name: 'Regulatory',
          description: 'Regulatory compliance practice'
        }
      ],
      contacts: [
        {
          id: 'contact-002',
          userId: 'user-005',
          name: 'Sarah Johnson',
          email: 'sjohnson@xyzlegal.com',
          role: 'Billing Director',
          phone: '312-555-6789',
          isActive: true,
          lastVerified: new Date('2023-08-15')
        }
      ],
      createdAt: new Date('2020-02-15'),
      updatedAt: new Date('2023-02-10')
    },
    {
      id: 'firm-003',
      name: 'Smith & Jones LLP',
      type: 'LawFirm',
      domain: 'smithjones.com',
      settings: {
        rateRules: {},
        approvalWorkflow: {},
        afaTarget: 0,
        defaultCurrency: 'USD'
      },
      offices: [
        {
          id: 'office-005',
          name: 'Boston',
          city: 'Boston',
          state: 'MA',
          country: 'USA',
          region: 'Northeast'
        },
        {
          id: 'office-006',
          name: 'San Francisco',
          city: 'San Francisco',
          state: 'CA',
          country: 'USA',
          region: 'West'
        }
      ],
      departments: [
        {
          id: 'dept-005',
          name: 'Employment',
          description: 'Employment and labor practice'
        },
        {
          id: 'dept-006',
          name: 'Finance',
          description: 'Banking and finance practice'
        }
      ],
      contacts: [
        {
          id: 'contact-003',
          userId: 'user-009',
          name: 'Michael Wilson',
          email: 'mwilson@smithjones.com',
          role: 'CFO',
          phone: '617-555-4321',
          isActive: true,
          lastVerified: new Date('2023-07-20')
        }
      ],
      createdAt: new Date('2020-03-10'),
      updatedAt: new Date('2023-03-05')
    }
  ],
  
  clients: [
    {
      id: 'client-001',
      name: 'Acme Corporation',
      type: 'Client',
      domain: 'acme.com',
      settings: {
        rateRules: {
          freezePeriod: 90,
          noticeRequired: 60,
          maxIncreasePercent: 5,
          submissionWindow: {
            startMonth: 10,
            startDay: 1,
            endMonth: 12,
            endDay: 31
          }
        },
        approvalWorkflow: {
          requireApproval: true,
          approverIds: ['user-016', 'user-017']
        },
        afaTarget: 70,
        defaultCurrency: 'USD'
      },
      offices: [
        {
          id: 'office-007',
          name: 'Headquarters',
          city: 'New York',
          state: 'NY',
          country: 'USA',
          region: 'Northeast'
        }
      ],
      departments: [
        {
          id: 'dept-007',
          name: 'Legal',
          description: 'Legal department'
        },
        {
          id: 'dept-008',
          name: 'Compliance',
          description: 'Compliance department'
        }
      ],
      contacts: [
        {
          id: 'contact-004',
          userId: 'user-013',
          name: 'Robert Chen',
          email: 'rchen@acme.com',
          role: 'General Counsel',
          phone: '212-555-8765',
          isActive: true,
          lastVerified: new Date('2023-08-01')
        }
      ],
      createdAt: new Date('2020-01-15'),
      updatedAt: new Date('2023-01-20')
    },
    {
      id: 'client-002',
      name: 'Global Industries Inc.',
      type: 'Client',
      domain: 'globalind.com',
      settings: {
        rateRules: {
          freezePeriod: 120,
          noticeRequired: 90,
          maxIncreasePercent: 4,
          submissionWindow: {
            startMonth: 9,
            startDay: 1,
            endMonth: 11,
            endDay: 30
          }
        },
        approvalWorkflow: {
          requireApproval: true,
          approverIds: ['user-020', 'user-021']
        },
        afaTarget: 65,
        defaultCurrency: 'USD'
      },
      offices: [
        {
          id: 'office-008',
          name: 'Headquarters',
          city: 'Chicago',
          state: 'IL',
          country: 'USA',
          region: 'Midwest'
        }
      ],
      departments: [
        {
          id: 'dept-009',
          name: 'Legal',
          description: 'Legal department'
        }
      ],
      contacts: [
        {
          id: 'contact-005',
          userId: 'user-017',
          name: 'Jessica Martinez',
          email: 'jmartinez@globalind.com',
          role: 'Deputy General Counsel',
          phone: '312-555-2468',
          isActive: true,
          lastVerified: new Date('2023-07-15')
        }
      ],
      createdAt: new Date('2020-02-01'),
      updatedAt: new Date('2023-02-15')
    },
    {
      id: 'client-003',
      name: 'Tech Innovations LLC',
      type: 'Client',
      domain: 'techinnovations.com',
      settings: {
        rateRules: {
          freezePeriod: 60,
          noticeRequired: 45,
          maxIncreasePercent: 6,
          submissionWindow: {
            startMonth: 11,
            startDay: 1,
            endMonth: 12,
            endDay: 31
          }
        },
        approvalWorkflow: {
          requireApproval: true,
          approverIds: ['user-024']
        },
        afaTarget: 50,
        defaultCurrency: 'USD'
      },
      offices: [
        {
          id: 'office-009',
          name: 'Headquarters',
          city: 'San Francisco',
          state: 'CA',
          country: 'USA',
          region: 'West'
        }
      ],
      departments: [
        {
          id: 'dept-010',
          name: 'Legal',
          description: 'Legal department'
        }
      ],
      contacts: [
        {
          id: 'contact-006',
          userId: 'user-021',
          name: 'David Wong',
          email: 'dwong@techinnovations.com',
          role: 'General Counsel',
          phone: '415-555-3698',
          isActive: true,
          lastVerified: new Date('2023-06-20')
        }
      ],
      createdAt: new Date('2020-03-15'),
      updatedAt: new Date('2023-03-10')
    }
  ]
};

// Mock Users with different roles
export const mockUsers = {
  lawFirmUsers: [
    {
      id: 'user-001',
      email: 'jsmith@abclaw.com',
      name: 'John Smith',
      organizationId: 'firm-001',
      organization: mockOrganizations.lawFirms[0],
      role: 'OrganizationAdministrator',
      permissions: ['ManageUsers', 'ManageOrganization', 'SubmitRates', 'ViewRates', 'ViewAnalytics'],
      isContact: true,
      lastVerified: new Date('2023-09-01'),
      createdAt: new Date('2021-01-15'),
      updatedAt: new Date('2023-09-01')
    },
    {
      id: 'user-002',
      email: 'agreen@abclaw.com',
      name: 'Alice Green',
      organizationId: 'firm-001',
      organization: mockOrganizations.lawFirms[0],
      role: 'RateAdministrator',
      permissions: ['SubmitRates', 'ViewRates', 'ViewAnalytics'],
      isContact: false,
      lastVerified: new Date('2023-08-15'),
      createdAt: new Date('2021-02-01'),
      updatedAt: new Date('2023-08-15')
    },
    {
      id: 'user-003',
      email: 'mwilliams@abclaw.com',
      name: 'Mark Williams',
      organizationId: 'firm-001',
      organization: mockOrganizations.lawFirms[0],
      role: 'StandardUser',
      permissions: ['ViewRates'],
      isContact: false,
      lastVerified: new Date('2023-07-20'),
      createdAt: new Date('2021-03-10'),
      updatedAt: new Date('2023-07-20')
    },
    {
      id: 'user-004',
      email: 'llee@abclaw.com',
      name: 'Linda Lee',
      organizationId: 'firm-001',
      organization: mockOrganizations.lawFirms[0],
      role: 'Approver',
      permissions: ['ViewRates', 'ApproveRates'],
      isContact: false,
      lastVerified: new Date('2023-06-15'),
      createdAt: new Date('2021-04-05'),
      updatedAt: new Date('2023-06-15')
    },
    // XYZ Legal Group Users
    {
      id: 'user-005',
      email: 'sjohnson@xyzlegal.com',
      name: 'Sarah Johnson',
      organizationId: 'firm-002',
      organization: mockOrganizations.lawFirms[1],
      role: 'OrganizationAdministrator',
      permissions: ['ManageUsers', 'ManageOrganization', 'SubmitRates', 'ViewRates', 'ViewAnalytics'],
      isContact: true,
      lastVerified: new Date('2023-08-15'),
      createdAt: new Date('2021-01-20'),
      updatedAt: new Date('2023-08-15')
    },
    {
      id: 'user-006',
      email: 'tbrown@xyzlegal.com',
      name: 'Tom Brown',
      organizationId: 'firm-002',
      organization: mockOrganizations.lawFirms[1],
      role: 'RateAdministrator',
      permissions: ['SubmitRates', 'ViewRates', 'ViewAnalytics'],
      isContact: false,
      lastVerified: new Date('2023-07-25'),
      createdAt: new Date('2021-02-10'),
      updatedAt: new Date('2023-07-25')
    },
    {
      id: 'user-007',
      email: 'jgarcia@xyzlegal.com',
      name: 'Julia Garcia',
      organizationId: 'firm-002',
      organization: mockOrganizations.lawFirms[1],
      role: 'StandardUser',
      permissions: ['ViewRates'],
      isContact: false,
      lastVerified: new Date('2023-06-30'),
      createdAt: new Date('2021-03-15'),
      updatedAt: new Date('2023-06-30')
    },
    {
      id: 'user-008',
      email: 'rnguyen@xyzlegal.com',
      name: 'Richard Nguyen',
      organizationId: 'firm-002',
      organization: mockOrganizations.lawFirms[1],
      role: 'Approver',
      permissions: ['ViewRates', 'ApproveRates'],
      isContact: false,
      lastVerified: new Date('2023-05-20'),
      createdAt: new Date('2021-04-10'),
      updatedAt: new Date('2023-05-20')
    },
    // Smith & Jones LLP Users
    {
      id: 'user-009',
      email: 'mwilson@smithjones.com',
      name: 'Michael Wilson',
      organizationId: 'firm-003',
      organization: mockOrganizations.lawFirms[2],
      role: 'OrganizationAdministrator',
      permissions: ['ManageUsers', 'ManageOrganization', 'SubmitRates', 'ViewRates', 'ViewAnalytics'],
      isContact: true,
      lastVerified: new Date('2023-07-20'),
      createdAt: new Date('2021-01-25'),
      updatedAt: new Date('2023-07-20')
    },
    {
      id: 'user-010',
      email: 'kpatel@smithjones.com',
      name: 'Kiran Patel',
      organizationId: 'firm-003',
      organization: mockOrganizations.lawFirms[2],
      role: 'RateAdministrator',
      permissions: ['SubmitRates', 'ViewRates', 'ViewAnalytics'],
      isContact: false,
      lastVerified: new Date('2023-06-20'),
      createdAt: new Date('2021-02-15'),
      updatedAt: new Date('2023-06-20')
    },
    {
      id: 'user-011',
      email: 'scohen@smithjones.com',
      name: 'Samantha Cohen',
      organizationId: 'firm-003',
      organization: mockOrganizations.lawFirms[2],
      role: 'StandardUser',
      permissions: ['ViewRates'],
      isContact: false,
      lastVerified: new Date('2023-05-15'),
      createdAt: new Date('2021-03-20'),
      updatedAt: new Date('2023-05-15')
    },
    {
      id: 'user-012',
      email: 'jroberts@smithjones.com',
      name: 'James Roberts',
      organizationId: 'firm-003',
      organization: mockOrganizations.lawFirms[2],
      role: 'Approver',
      permissions: ['ViewRates', 'ApproveRates'],
      isContact: false,
      lastVerified: new Date('2023-04-10'),
      createdAt: new Date('2021-04-15'),
      updatedAt: new Date('2023-04-10')
    }
  ],
  
  clientUsers: [
    // Acme Corporation Users
    {
      id: 'user-013',
      email: 'rchen@acme.com',
      name: 'Robert Chen',
      organizationId: 'client-001',
      organization: mockOrganizations.clients[0],
      role: 'OrganizationAdministrator',
      permissions: ['ManageUsers', 'ManageOrganization', 'ViewRates', 'ApproveRates', 'CounterProposeRates', 'ViewAnalytics', 'ManageOCG'],
      isContact: true,
      lastVerified: new Date('2023-08-01'),
      createdAt: new Date('2021-01-10'),
      updatedAt: new Date('2023-08-01')
    },
    {
      id: 'user-014',
      email: 'dsmith@acme.com',
      name: 'Daniel Smith',
      organizationId: 'client-001',
      organization: mockOrganizations.clients[0],
      role: 'RateAdministrator',
      permissions: ['ViewRates', 'ApproveRates', 'CounterProposeRates', 'ViewAnalytics'],
      isContact: false,
      lastVerified: new Date('2023-07-10'),
      createdAt: new Date('2021-02-05'),
      updatedAt: new Date('2023-07-10')
    },
    {
      id: 'user-015',
      email: 'jpark@acme.com',
      name: 'Jennifer Park',
      organizationId: 'client-001',
      organization: mockOrganizations.clients[0],
      role: 'Analyst',
      permissions: ['ViewRates', 'ViewAnalytics'],
      isContact: false,
      lastVerified: new Date('2023-06-05'),
      createdAt: new Date('2021-03-01'),
      updatedAt: new Date('2023-06-05')
    },
    {
      id: 'user-016',
      email: 'wmiller@acme.com',
      name: 'William Miller',
      organizationId: 'client-001',
      organization: mockOrganizations.clients[0],
      role: 'Approver',
      permissions: ['ViewRates', 'ApproveRates'],
      isContact: false,
      lastVerified: new Date('2023-05-01'),
      createdAt: new Date('2021-04-01'),
      updatedAt: new Date('2023-05-01')
    },
    // Global Industries Users
    {
      id: 'user-017',
      email: 'jmartinez@globalind.com',
      name: 'Jessica Martinez',
      organizationId: 'client-002',
      organization: mockOrganizations.clients[1],
      role: 'OrganizationAdministrator',
      permissions: ['ManageUsers', 'ManageOrganization', 'ViewRates', 'ApproveRates', 'CounterProposeRates', 'ViewAnalytics', 'ManageOCG'],
      isContact: true,
      lastVerified: new Date('2023-07-15'),
      createdAt: new Date('2021-01-15'),
      updatedAt: new Date('2023-07-15')
    },
    {
      id: 'user-018',
      email: 'akim@globalind.com',
      name: 'Alex Kim',
      organizationId: 'client-002',
      organization: mockOrganizations.clients[1],
      role: 'RateAdministrator',
      permissions: ['ViewRates', 'ApproveRates', 'CounterProposeRates', 'ViewAnalytics'],
      isContact: false,
      lastVerified: new Date('2023-06-10'),
      createdAt: new Date('2021-02-10'),
      updatedAt: new Date('2023-06-10')
    },
    {
      id: 'user-019',
      email: 'rtaylor@globalind.com',
      name: 'Rachel Taylor',
      organizationId: 'client-002',
      organization: mockOrganizations.clients[1],
      role: 'Analyst',
      permissions: ['ViewRates', 'ViewAnalytics'],
      isContact: false,
      lastVerified: new Date('2023-05-05'),
      createdAt: new Date('2021-03-05'),
      updatedAt: new Date('2023-05-05')
    },
    {
      id: 'user-020',
      email: 'bjohnson@globalind.com',
      name: 'Brian Johnson',
      organizationId: 'client-002',
      organization: mockOrganizations.clients[1],
      role: 'Approver',
      permissions: ['ViewRates', 'ApproveRates'],
      isContact: false,
      lastVerified: new Date('2023-04-01'),
      createdAt: new Date('2021-04-05'),
      updatedAt: new Date('2023-04-01')
    },
    // Tech Innovations Users
    {
      id: 'user-021',
      email: 'dwong@techinnovations.com',
      name: 'David Wong',
      organizationId: 'client-003',
      organization: mockOrganizations.clients[2],
      role: 'OrganizationAdministrator',
      permissions: ['ManageUsers', 'ManageOrganization', 'ViewRates', 'ApproveRates', 'CounterProposeRates', 'ViewAnalytics', 'ManageOCG'],
      isContact: true,
      lastVerified: new Date('2023-06-20'),
      createdAt: new Date('2021-01-20'),
      updatedAt: new Date('2023-06-20')
    },
    {
      id: 'user-022',
      email: 'lrodriguez@techinnovations.com',
      name: 'Laura Rodriguez',
      organizationId: 'client-003',
      organization: mockOrganizations.clients[2],
      role: 'RateAdministrator',
      permissions: ['ViewRates', 'ApproveRates', 'CounterProposeRates', 'ViewAnalytics'],
      isContact: false,
      lastVerified: new Date('2023-05-15'),
      createdAt: new Date('2021-02-15'),
      updatedAt: new Date('2023-05-15')
    },
    {
      id: 'user-023',
      email: 'ssinha@techinnovations.com',
      name: 'Sanjay Sinha',
      organizationId: 'client-003',
      organization: mockOrganizations.clients[2],
      role: 'Analyst',
      permissions: ['ViewRates', 'ViewAnalytics'],
      isContact: false,
      lastVerified: new Date('2023-04-10'),
      createdAt: new Date('2021-03-10'),
      updatedAt: new Date('2023-04-10')
    },
    {
      id: 'user-024',
      email: 'omorgan@techinnovations.com',
      name: 'Olivia Morgan',
      organizationId: 'client-003',
      organization: mockOrganizations.clients[2],
      role: 'Approver',
      permissions: ['ViewRates', 'ApproveRates'],
      isContact: false,
      lastVerified: new Date('2023-03-05'),
      createdAt: new Date('2021-04-10'),
      updatedAt: new Date('2023-03-05')
    }
  ],
  
  adminUsers: [
    {
      id: 'user-025',
      email: 'admin@justicebid.com',
      name: 'Admin User',
      organizationId: 'admin-001',
      organization: {
        id: 'admin-001',
        name: 'Justice Bid',
        type: 'Admin',
        domain: 'justicebid.com',
        settings: {},
        offices: [],
        departments: [],
        contacts: [],
        createdAt: new Date('2020-01-01'),
        updatedAt: new Date('2020-01-01')
      },
      role: 'SystemAdministrator',
      permissions: ['ManageUsers', 'ManageOrganization', 'ViewRates', 'ApproveRates', 'CounterProposeRates', 'ViewAnalytics', 'ManageOCG', 'ManageIntegrations'],
      isContact: false,
      lastVerified: new Date('2023-09-01'),
      createdAt: new Date('2020-01-01'),
      updatedAt: new Date('2023-09-01')
    }
  ]
};

// Mock Staff Classes
export const mockStaffClasses = [
  {
    id: 'staffclass-001',
    organizationId: 'client-001',
    name: 'Partner',
    experienceType: 'YearsInRole',
    minExperience: 10,
    maxExperience: null
  },
  {
    id: 'staffclass-002',
    organizationId: 'client-001',
    name: 'Senior Associate',
    experienceType: 'YearsInRole',
    minExperience: 5,
    maxExperience: 10
  },
  {
    id: 'staffclass-003',
    organizationId: 'client-001',
    name: 'Junior Associate',
    experienceType: 'YearsInRole',
    minExperience: 0,
    maxExperience: 5
  },
  {
    id: 'staffclass-004',
    organizationId: 'client-001',
    name: 'Paralegal',
    experienceType: 'YearsInRole',
    minExperience: 0,
    maxExperience: null
  },
  {
    id: 'staffclass-005',
    organizationId: 'client-002',
    name: 'Partner',
    experienceType: 'YearsInRole',
    minExperience: 8,
    maxExperience: null
  },
  {
    id: 'staffclass-006',
    organizationId: 'client-002',
    name: 'Senior Associate',
    experienceType: 'YearsInRole',
    minExperience: 4,
    maxExperience: 8
  },
  {
    id: 'staffclass-007',
    organizationId: 'client-002',
    name: 'Junior Associate',
    experienceType: 'YearsInRole',
    minExperience: 0,
    maxExperience: 4
  },
  {
    id: 'staffclass-008',
    organizationId: 'client-002',
    name: 'Paralegal',
    experienceType: 'YearsInRole',
    minExperience: 0,
    maxExperience: null
  },
  {
    id: 'staffclass-009',
    organizationId: 'client-003',
    name: 'Partner',
    experienceType: 'YearsInRole',
    minExperience: 10,
    maxExperience: null
  },
  {
    id: 'staffclass-010',
    organizationId: 'client-003',
    name: 'Senior Associate',
    experienceType: 'YearsInRole',
    minExperience: 5,
    maxExperience: 10
  },
  {
    id: 'staffclass-011',
    organizationId: 'client-003',
    name: 'Junior Associate',
    experienceType: 'YearsInRole',
    minExperience: 0,
    maxExperience: 5
  },
  {
    id: 'staffclass-012',
    organizationId: 'client-003',
    name: 'Paralegal',
    experienceType: 'YearsInRole',
    minExperience: 0,
    maxExperience: null
  }
];

// Mock Attorneys
export const mockAttorneys = [
  // ABC Law LLP Attorneys
  {
    id: 'attorney-001',
    name: 'James Smith',
    organizationId: 'firm-001',
    barDate: '2005-06-15',
    graduationDate: '2005-05-15',
    promotionDate: '2015-01-01',
    officeIds: ['office-001'],
    practiceAreas: ['Litigation', 'Corporate'],
    timekeeperIds: {
      'client-001': 'TK0001',
      'client-002': 'TK0023',
      'client-003': 'TK0045'
    },
    unicourtId: 'UC123456',
    staffClassId: 'staffclass-001',
    performanceData: {
      unicourt: {
        caseCount: 87,
        winRate: 0.76,
        caseTypes: {
          'Commercial': 45,
          'IP': 22,
          'Employment': 20
        },
        courts: {
          'SDNY': 40,
          'EDNY': 25,
          'DNJ': 22
        },
        percentile: 85
      },
      ratings: [
        {
          clientId: 'client-001',
          value: 4.5,
          comment: 'Excellent strategic thinking',
          date: '2023-06-01'
        }
      ],
      billingMetrics: {
        hours: 1850,
        fees: 1387500,
        matters: 12,
        utilization: 0.92,
        realization: 0.95,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-01-15',
    updatedAt: '2023-08-01'
  },
  {
    id: 'attorney-002',
    name: 'Amanda Jones',
    organizationId: 'firm-001',
    barDate: '2010-09-20',
    graduationDate: '2010-05-30',
    promotionDate: '2018-01-01',
    officeIds: ['office-001'],
    practiceAreas: ['Corporate', 'M&A'],
    timekeeperIds: {
      'client-001': 'TK0002',
      'client-002': 'TK0024'
    },
    unicourtId: 'UC123457',
    staffClassId: 'staffclass-001',
    performanceData: {
      unicourt: {
        caseCount: 42,
        winRate: 0.81,
        caseTypes: {
          'Commercial': 30,
          'Securities': 12
        },
        courts: {
          'SDNY': 25,
          'Delaware': 17
        },
        percentile: 88
      },
      ratings: [
        {
          clientId: 'client-001',
          value: 4.7,
          comment: 'Exceptional deal execution',
          date: '2023-05-15'
        }
      ],
      billingMetrics: {
        hours: 1920,
        fees: 1248000,
        matters: 8,
        utilization: 0.95,
        realization: 0.97,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-01-16',
    updatedAt: '2023-07-15'
  },
  {
    id: 'attorney-003',
    name: 'Michael Davis',
    organizationId: 'firm-001',
    barDate: '2015-12-01',
    graduationDate: '2015-05-20',
    promotionDate: '2021-01-01',
    officeIds: ['office-002'],
    practiceAreas: ['Litigation', 'Environmental'],
    timekeeperIds: {
      'client-001': 'TK0003',
      'client-003': 'TK0046'
    },
    unicourtId: 'UC123458',
    staffClassId: 'staffclass-002',
    performanceData: {
      unicourt: {
        caseCount: 35,
        winRate: 0.72,
        caseTypes: {
          'Environmental': 20,
          'Commercial': 15
        },
        courts: {
          'CDCA': 22,
          'NDCA': 13
        },
        percentile: 75
      },
      ratings: [
        {
          clientId: 'client-001',
          value: 4.2,
          comment: 'Strong technical knowledge',
          date: '2023-04-10'
        }
      ],
      billingMetrics: {
        hours: 1780,
        fees: 979000,
        matters: 10,
        utilization: 0.88,
        realization: 0.93,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-01-20',
    updatedAt: '2023-06-10'
  },
  {
    id: 'attorney-004',
    name: 'Sarah Wilson',
    organizationId: 'firm-001',
    barDate: '2018-07-10',
    graduationDate: '2018-05-15',
    promotionDate: null,
    officeIds: ['office-001'],
    practiceAreas: ['Corporate', 'Finance'],
    timekeeperIds: {
      'client-002': 'TK0025',
      'client-003': 'TK0047'
    },
    unicourtId: 'UC123459',
    staffClassId: 'staffclass-003',
    performanceData: {
      unicourt: {
        caseCount: 12,
        winRate: 0.67,
        caseTypes: {
          'Commercial': 8,
          'Finance': 4
        },
        courts: {
          'SDNY': 7,
          'EDNY': 5
        },
        percentile: 65
      },
      ratings: [
        {
          clientId: 'client-002',
          value: 4.0,
          comment: 'Reliable and thorough',
          date: '2023-03-20'
        }
      ],
      billingMetrics: {
        hours: 1950,
        fees: 877500,
        matters: 7,
        utilization: 0.94,
        realization: 0.90,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-02-01',
    updatedAt: '2023-05-05'
  },
  
  // XYZ Legal Group Attorneys
  {
    id: 'attorney-005',
    name: 'Robert Johnson',
    organizationId: 'firm-002',
    barDate: '2000-10-12',
    graduationDate: '2000-05-20',
    promotionDate: '2010-01-01',
    officeIds: ['office-003'],
    practiceAreas: ['Intellectual Property', 'Patents'],
    timekeeperIds: {
      'client-001': 'TK0004',
      'client-002': 'TK0026',
      'client-003': 'TK0048'
    },
    unicourtId: 'UC123460',
    staffClassId: 'staffclass-001',
    performanceData: {
      unicourt: {
        caseCount: 105,
        winRate: 0.79,
        caseTypes: {
          'Patent': 75,
          'Copyright': 20,
          'Trademark': 10
        },
        courts: {
          'Federal Circuit': 60,
          'NDIL': 25,
          'EDTX': 20
        },
        percentile: 90
      },
      ratings: [
        {
          clientId: 'client-001',
          value: 4.8,
          comment: 'Outstanding patent expertise',
          date: '2023-06-05'
        }
      ],
      billingMetrics: {
        hours: 1800,
        fees: 1350000,
        matters: 15,
        utilization: 0.90,
        realization: 0.96,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-01-15',
    updatedAt: '2023-08-05'
  },
  {
    id: 'attorney-006',
    name: 'Emily Nguyen',
    organizationId: 'firm-002',
    barDate: '2009-05-30',
    graduationDate: '2009-05-15',
    promotionDate: '2017-01-01',
    officeIds: ['office-004'],
    practiceAreas: ['Regulatory', 'Healthcare'],
    timekeeperIds: {
      'client-002': 'TK0027',
      'client-003': 'TK0049'
    },
    unicourtId: 'UC123461',
    staffClassId: 'staffclass-001',
    performanceData: {
      unicourt: {
        caseCount: 65,
        winRate: 0.82,
        caseTypes: {
          'Healthcare': 45,
          'Administrative': 20
        },
        courts: {
          'DDC': 40,
          'EDVA': 25
        },
        percentile: 87
      },
      ratings: [
        {
          clientId: 'client-002',
          value: 4.6,
          comment: 'Excellent regulatory knowledge',
          date: '2023-05-10'
        }
      ],
      billingMetrics: {
        hours: 1880,
        fees: 1222000,
        matters: 12,
        utilization: 0.93,
        realization: 0.95,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-01-18',
    updatedAt: '2023-07-10'
  },
  {
    id: 'attorney-007',
    name: 'David Park',
    organizationId: 'firm-002',
    barDate: '2014-11-15',
    graduationDate: '2014-05-10',
    promotionDate: '2021-01-01',
    officeIds: ['office-003'],
    practiceAreas: ['Intellectual Property', 'Technology'],
    timekeeperIds: {
      'client-001': 'TK0005',
      'client-003': 'TK0050'
    },
    unicourtId: 'UC123462',
    staffClassId: 'staffclass-002',
    performanceData: {
      unicourt: {
        caseCount: 42,
        winRate: 0.74,
        caseTypes: {
          'Patent': 30,
          'Technology': 12
        },
        courts: {
          'NDIL': 25,
          'NDCA': 17
        },
        percentile: 78
      },
      ratings: [
        {
          clientId: 'client-001',
          value: 4.3,
          comment: 'Detailed and thorough',
          date: '2023-04-15'
        }
      ],
      billingMetrics: {
        hours: 1820,
        fees: 1001000,
        matters: 9,
        utilization: 0.90,
        realization: 0.92,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-01-25',
    updatedAt: '2023-06-15'
  },
  {
    id: 'attorney-008',
    name: 'Lisa Thompson',
    organizationId: 'firm-002',
    barDate: '2017-12-20',
    graduationDate: '2017-05-20',
    promotionDate: null,
    officeIds: ['office-004'],
    practiceAreas: ['Regulatory', 'Environmental'],
    timekeeperIds: {
      'client-002': 'TK0028'
    },
    unicourtId: 'UC123463',
    staffClassId: 'staffclass-003',
    performanceData: {
      unicourt: {
        caseCount: 18,
        winRate: 0.72,
        caseTypes: {
          'Environmental': 12,
          'Administrative': 6
        },
        courts: {
          'DDC': 10,
          'EDVA': 8
        },
        percentile: 70
      },
      ratings: [
        {
          clientId: 'client-002',
          value: 4.1,
          comment: 'Solid regulatory analysis',
          date: '2023-03-25'
        }
      ],
      billingMetrics: {
        hours: 1920,
        fees: 864000,
        matters: 6,
        utilization: 0.95,
        realization: 0.89,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-02-05',
    updatedAt: '2023-05-15'
  },
  
  // Smith & Jones LLP Attorneys
  {
    id: 'attorney-009',
    name: 'Thomas Miller',
    organizationId: 'firm-003',
    barDate: '2003-02-28',
    graduationDate: '2002-05-25',
    promotionDate: '2013-01-01',
    officeIds: ['office-005'],
    practiceAreas: ['Employment', 'Labor'],
    timekeeperIds: {
      'client-001': 'TK0006',
      'client-002': 'TK0029',
      'client-003': 'TK0051'
    },
    unicourtId: 'UC123464',
    staffClassId: 'staffclass-001',
    performanceData: {
      unicourt: {
        caseCount: 92,
        winRate: 0.77,
        caseTypes: {
          'Employment': 65,
          'Labor': 27
        },
        courts: {
          'DMA': 45,
          'EDNC': 25,
          'DME': 22
        },
        percentile: 83
      },
      ratings: [
        {
          clientId: 'client-001',
          value: 4.5,
          comment: 'Excellent employment counsel',
          date: '2023-06-10'
        }
      ],
      billingMetrics: {
        hours: 1750,
        fees: 1225000,
        matters: 18,
        utilization: 0.87,
        realization: 0.94,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-01-15',
    updatedAt: '2023-08-10'
  },
  {
    id: 'attorney-010',
    name: 'Karen Rodriguez',
    organizationId: 'firm-003',
    barDate: '2008-07-15',
    graduationDate: '2008-05-10',
    promotionDate: '2016-01-01',
    officeIds: ['office-006'],
    practiceAreas: ['Finance', 'Banking'],
    timekeeperIds: {
      'client-002': 'TK0030',
      'client-003': 'TK0052'
    },
    unicourtId: 'UC123465',
    staffClassId: 'staffclass-001',
    performanceData: {
      unicourt: {
        caseCount: 68,
        winRate: 0.85,
        caseTypes: {
          'Finance': 45,
          'Banking': 23
        },
        courts: {
          'NDCA': 40,
          'CDCA': 28
        },
        percentile: 92
      },
      ratings: [
        {
          clientId: 'client-002',
          value: 4.9,
          comment: 'Exceptional finance lawyer',
          date: '2023-05-20'
        }
      ],
      billingMetrics: {
        hours: 1830,
        fees: 1281000,
        matters: 10,
        utilization: 0.91,
        realization: 0.97,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-01-20',
    updatedAt: '2023-07-20'
  },
  {
    id: 'attorney-011',
    name: 'Jason Lee',
    organizationId: 'firm-003',
    barDate: '2013-09-10',
    graduationDate: '2013-05-15',
    promotionDate: '2020-01-01',
    officeIds: ['office-005'],
    practiceAreas: ['Employment', 'Litigation'],
    timekeeperIds: {
      'client-001': 'TK0007',
      'client-003': 'TK0053'
    },
    unicourtId: 'UC123466',
    staffClassId: 'staffclass-002',
    performanceData: {
      unicourt: {
        caseCount: 48,
        winRate: 0.73,
        caseTypes: {
          'Employment': 35,
          'General Litigation': 13
        },
        courts: {
          'DMA': 30,
          'DNH': 18
        },
        percentile: 76
      },
      ratings: [
        {
          clientId: 'client-001',
          value: 4.2,
          comment: 'Very responsive and practical',
          date: '2023-04-20'
        }
      ],
      billingMetrics: {
        hours: 1880,
        fees: 1034000,
        matters: 12,
        utilization: 0.93,
        realization: 0.91,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-01-30',
    updatedAt: '2023-06-20'
  },
  {
    id: 'attorney-012',
    name: 'Andrea White',
    organizationId: 'firm-003',
    barDate: '2016-12-15',
    graduationDate: '2016-05-20',
    promotionDate: null,
    officeIds: ['office-006'],
    practiceAreas: ['Finance', 'Corporate'],
    timekeeperIds: {
      'client-002': 'TK0031'
    },
    unicourtId: 'UC123467',
    staffClassId: 'staffclass-003',
    performanceData: {
      unicourt: {
        caseCount: 22,
        winRate: 0.68,
        caseTypes: {
          'Finance': 15,
          'Corporate': 7
        },
        courts: {
          'NDCA': 12,
          'CDCA': 10
        },
        percentile: 68
      },
      ratings: [
        {
          clientId: 'client-002',
          value: 4.0,
          comment: 'Diligent and detail-oriented',
          date: '2023-03-30'
        }
      ],
      billingMetrics: {
        hours: 1950,
        fees: 877500,
        matters: 7,
        utilization: 0.96,
        realization: 0.88,
        period: 'LAST_12_MONTHS'
      }
    },
    createdAt: '2021-02-10',
    updatedAt: '2023-05-25'
  }
];

// Mock Rate Data
export const mockRates = {
  // Current approved rates
  currentRates: [
    // ABC Law LLP - Acme Corporation rates
    {
      id: 'rate-001',
      attorneyId: 'attorney-001',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-001',
      officeId: 'office-001',
      amount: 750,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2023-01-01',
      expirationDate: '2023-12-31',
      status: 'APPROVED',
      history: [
        {
          amount: 750,
          type: 'APPROVED',
          status: 'APPROVED',
          timestamp: '2022-11-15T14:30:00Z',
          userId: 'user-013',
          message: 'Approved as proposed'
        }
      ],
      createdAt: '2022-10-15T10:00:00Z',
      updatedAt: '2022-11-15T14:30:00Z'
    },
    {
      id: 'rate-002',
      attorneyId: 'attorney-002',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-001',
      officeId: 'office-001',
      amount: 650,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2023-01-01',
      expirationDate: '2023-12-31',
      status: 'APPROVED',
      history: [
        {
          amount: 650,
          type: 'APPROVED',
          status: 'APPROVED',
          timestamp: '2022-11-15T14:30:00Z',
          userId: 'user-013',
          message: 'Approved as proposed'
        }
      ],
      createdAt: '2022-10-15T10:00:00Z',
      updatedAt: '2022-11-15T14:30:00Z'
    },
    {
      id: 'rate-003',
      attorneyId: 'attorney-003',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-002',
      officeId: 'office-002',
      amount: 550,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2023-01-01',
      expirationDate: '2023-12-31',
      status: 'APPROVED',
      history: [
        {
          amount: 550,
          type: 'APPROVED',
          status: 'APPROVED',
          timestamp: '2022-11-15T14:30:00Z',
          userId: 'user-013',
          message: 'Approved as proposed'
        }
      ],
      createdAt: '2022-10-15T10:00:00Z',
      updatedAt: '2022-11-15T14:30:00Z'
    },
    
    // XYZ Legal - Global Industries rates
    {
      id: 'rate-004',
      attorneyId: 'attorney-005',
      clientId: 'client-002',
      firmId: 'firm-002',
      staffClassId: 'staffclass-005',
      officeId: 'office-003',
      amount: 720,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2023-01-01',
      expirationDate: '2023-12-31',
      status: 'APPROVED',
      history: [
        {
          amount: 720,
          type: 'APPROVED',
          status: 'APPROVED',
          timestamp: '2022-10-20T11:45:00Z',
          userId: 'user-017',
          message: 'Approved after negotiation'
        }
      ],
      createdAt: '2022-09-10T09:30:00Z',
      updatedAt: '2022-10-20T11:45:00Z'
    },
    {
      id: 'rate-005',
      attorneyId: 'attorney-006',
      clientId: 'client-002',
      firmId: 'firm-002',
      staffClassId: 'staffclass-005',
      officeId: 'office-004',
      amount: 650,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2023-01-01',
      expirationDate: '2023-12-31',
      status: 'APPROVED',
      history: [
        {
          amount: 650,
          type: 'APPROVED',
          status: 'APPROVED',
          timestamp: '2022-10-20T11:45:00Z',
          userId: 'user-017',
          message: 'Approved after negotiation'
        }
      ],
      createdAt: '2022-09-10T09:30:00Z',
      updatedAt: '2022-10-20T11:45:00Z'
    },
    
    // Smith & Jones - Tech Innovations rates
    {
      id: 'rate-006',
      attorneyId: 'attorney-009',
      clientId: 'client-003',
      firmId: 'firm-003',
      staffClassId: 'staffclass-009',
      officeId: 'office-005',
      amount: 680,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2023-01-01',
      expirationDate: '2023-12-31',
      status: 'APPROVED',
      history: [
        {
          amount: 680,
          type: 'APPROVED',
          status: 'APPROVED',
          timestamp: '2022-12-05T16:15:00Z',
          userId: 'user-021',
          message: 'Approved with standard increase'
        }
      ],
      createdAt: '2022-11-01T14:00:00Z',
      updatedAt: '2022-12-05T16:15:00Z'
    },
    {
      id: 'rate-007',
      attorneyId: 'attorney-010',
      clientId: 'client-003',
      firmId: 'firm-003',
      staffClassId: 'staffclass-009',
      officeId: 'office-006',
      amount: 660,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2023-01-01',
      expirationDate: '2023-12-31',
      status: 'APPROVED',
      history: [
        {
          amount: 660,
          type: 'APPROVED',
          status: 'APPROVED',
          timestamp: '2022-12-05T16:15:00Z',
          userId: 'user-021',
          message: 'Approved with standard increase'
        }
      ],
      createdAt: '2022-11-01T14:00:00Z',
      updatedAt: '2022-12-05T16:15:00Z'
    }
  ],
  
  // Historical rates (prior years)
  historicalRates: [
    // James Smith historical rates
    {
      id: 'hist-rate-001',
      attorneyId: 'attorney-001',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-001',
      officeId: 'office-001',
      amount: 725,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2022-01-01',
      expirationDate: '2022-12-31',
      status: 'APPROVED',
      history: [],
      createdAt: '2021-10-15T10:00:00Z',
      updatedAt: '2021-11-20T14:30:00Z'
    },
    {
      id: 'hist-rate-002',
      attorneyId: 'attorney-001',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-001',
      officeId: 'office-001',
      amount: 700,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2021-01-01',
      expirationDate: '2021-12-31',
      status: 'APPROVED',
      history: [],
      createdAt: '2020-10-10T11:30:00Z',
      updatedAt: '2020-11-15T09:45:00Z'
    },
    {
      id: 'hist-rate-003',
      attorneyId: 'attorney-001',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-001',
      officeId: 'office-001',
      amount: 675,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2020-01-01',
      expirationDate: '2020-12-31',
      status: 'APPROVED',
      history: [],
      createdAt: '2019-10-05T13:15:00Z',
      updatedAt: '2019-11-10T16:20:00Z'
    },
    
    // Robert Johnson historical rates
    {
      id: 'hist-rate-004',
      attorneyId: 'attorney-005',
      clientId: 'client-002',
      firmId: 'firm-002',
      staffClassId: 'staffclass-005',
      officeId: 'office-003',
      amount: 695,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2022-01-01',
      expirationDate: '2022-12-31',
      status: 'APPROVED',
      history: [],
      createdAt: '2021-09-12T10:30:00Z',
      updatedAt: '2021-10-18T15:45:00Z'
    },
    {
      id: 'hist-rate-005',
      attorneyId: 'attorney-005',
      clientId: 'client-002',
      firmId: 'firm-002',
      staffClassId: 'staffclass-005',
      officeId: 'office-003',
      amount: 670,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2021-01-01',
      expirationDate: '2021-12-31',
      status: 'APPROVED',
      history: [],
      createdAt: '2020-09-15T11:00:00Z',
      updatedAt: '2020-10-20T14:30:00Z'
    },
    
    // Thomas Miller historical rates
    {
      id: 'hist-rate-006',
      attorneyId: 'attorney-009',
      clientId: 'client-003',
      firmId: 'firm-003',
      staffClassId: 'staffclass-009',
      officeId: 'office-005',
      amount: 650,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2022-01-01',
      expirationDate: '2022-12-31',
      status: 'APPROVED',
      history: [],
      createdAt: '2021-11-05T09:15:00Z',
      updatedAt: '2021-12-10T13:20:00Z'
    },
    {
      id: 'hist-rate-007',
      attorneyId: 'attorney-009',
      clientId: 'client-003',
      firmId: 'firm-003',
      staffClassId: 'staffclass-009',
      officeId: 'office-005',
      amount: 625,
      currency: 'USD',
      type: 'APPROVED',
      effectiveDate: '2021-01-01',
      expirationDate: '2021-12-31',
      status: 'APPROVED',
      history: [],
      createdAt: '2020-11-10T10:45:00Z',
      updatedAt: '2020-12-15T14:50:00Z'
    }
  ],
  
  // Proposed rates for 2024
  proposedRates: [
    // ABC Law proposed rates for Acme Corporation
    {
      id: 'prop-rate-001',
      attorneyId: 'attorney-001',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-001',
      officeId: 'office-001',
      amount: 795,
      currency: 'USD',
      type: 'PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'SUBMITTED',
      history: [
        {
          amount: 795,
          type: 'PROPOSED',
          status: 'SUBMITTED',
          timestamp: '2023-10-10T11:30:00Z',
          userId: 'user-001',
          message: 'Proposed 2024 rate with 6% increase'
        }
      ],
      createdAt: '2023-10-10T11:30:00Z',
      updatedAt: '2023-10-10T11:30:00Z'
    },
    {
      id: 'prop-rate-002',
      attorneyId: 'attorney-002',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-001',
      officeId: 'office-001',
      amount: 680,
      currency: 'USD',
      type: 'PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'SUBMITTED',
      history: [
        {
          amount: 680,
          type: 'PROPOSED',
          status: 'SUBMITTED',
          timestamp: '2023-10-10T11:30:00Z',
          userId: 'user-001',
          message: 'Proposed 2024 rate with 4.6% increase'
        }
      ],
      createdAt: '2023-10-10T11:30:00Z',
      updatedAt: '2023-10-10T11:30:00Z'
    },
    {
      id: 'prop-rate-003',
      attorneyId: 'attorney-003',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-002',
      officeId: 'office-002',
      amount: 575,
      currency: 'USD',
      type: 'PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'SUBMITTED',
      history: [
        {
          amount: 575,
          type: 'PROPOSED',
          status: 'SUBMITTED',
          timestamp: '2023-10-10T11:30:00Z',
          userId: 'user-001',
          message: 'Proposed 2024 rate with 4.5% increase'
        }
      ],
      createdAt: '2023-10-10T11:30:00Z',
      updatedAt: '2023-10-10T11:30:00Z'
    },
    
    // XYZ Legal proposed rates for Global Industries
    {
      id: 'prop-rate-004',
      attorneyId: 'attorney-005',
      clientId: 'client-002',
      firmId: 'firm-002',
      staffClassId: 'staffclass-005',
      officeId: 'office-003',
      amount: 750,
      currency: 'USD',
      type: 'PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'SUBMITTED',
      history: [
        {
          amount: 750,
          type: 'PROPOSED',
          status: 'SUBMITTED',
          timestamp: '2023-10-05T14:15:00Z',
          userId: 'user-005',
          message: 'Proposed 2024 rate with 4.2% increase'
        }
      ],
      createdAt: '2023-10-05T14:15:00Z',
      updatedAt: '2023-10-05T14:15:00Z'
    },
    {
      id: 'prop-rate-005',
      attorneyId: 'attorney-006',
      clientId: 'client-002',
      firmId: 'firm-002',
      staffClassId: 'staffclass-005',
      officeId: 'office-004',
      amount: 675,
      currency: 'USD',
      type: 'PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'SUBMITTED',
      history: [
        {
          amount: 675,
          type: 'PROPOSED',
          status: 'SUBMITTED',
          timestamp: '2023-10-05T14:15:00Z',
          userId: 'user-005',
          message: 'Proposed 2024 rate with 3.8% increase'
        }
      ],
      createdAt: '2023-10-05T14:15:00Z',
      updatedAt: '2023-10-05T14:15:00Z'
    },
    
    // Smith & Jones draft rates for Tech Innovations
    {
      id: 'prop-rate-006',
      attorneyId: 'attorney-009',
      clientId: 'client-003',
      firmId: 'firm-003',
      staffClassId: 'staffclass-009',
      officeId: 'office-005',
      amount: 700,
      currency: 'USD',
      type: 'PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'DRAFT',
      history: [
        {
          amount: 700,
          type: 'PROPOSED',
          status: 'DRAFT',
          timestamp: '2023-10-15T09:45:00Z',
          userId: 'user-009',
          message: 'Draft rate for 2024 with 2.9% increase'
        }
      ],
      createdAt: '2023-10-15T09:45:00Z',
      updatedAt: '2023-10-15T09:45:00Z'
    },
    {
      id: 'prop-rate-007',
      attorneyId: 'attorney-010',
      clientId: 'client-003',
      firmId: 'firm-003',
      staffClassId: 'staffclass-009',
      officeId: 'office-006',
      amount: 690,
      currency: 'USD',
      type: 'PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'DRAFT',
      history: [
        {
          amount: 690,
          type: 'PROPOSED',
          status: 'DRAFT',
          timestamp: '2023-10-15T09:45:00Z',
          userId: 'user-009',
          message: 'Draft rate for 2024 with 4.5% increase'
        }
      ],
      createdAt: '2023-10-15T09:45:00Z',
      updatedAt: '2023-10-15T09:45:00Z'
    }
  ],
  
  // Counter-proposed rates
  counterProposedRates: [
    // Acme Corporation counter-proposals to ABC Law
    {
      id: 'counter-rate-001',
      attorneyId: 'attorney-001',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-001',
      officeId: 'office-001',
      amount: 787,
      currency: 'USD',
      type: 'COUNTER_PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'UNDER_REVIEW',
      history: [
        {
          amount: 795,
          type: 'PROPOSED',
          status: 'SUBMITTED',
          timestamp: '2023-10-10T11:30:00Z',
          userId: 'user-001',
          message: 'Proposed 2024 rate with 6% increase'
        },
        {
          amount: 787,
          type: 'COUNTER_PROPOSED',
          status: 'UNDER_REVIEW',
          timestamp: '2023-10-20T15:45:00Z',
          userId: 'user-014',
          message: 'Counter-proposal within our 5% increase guideline'
        }
      ],
      createdAt: '2023-10-10T11:30:00Z',
      updatedAt: '2023-10-20T15:45:00Z'
    },
    {
      id: 'counter-rate-002',
      attorneyId: 'attorney-002',
      clientId: 'client-001',
      firmId: 'firm-001',
      staffClassId: 'staffclass-001',
      officeId: 'office-001',
      amount: 680,
      currency: 'USD',
      type: 'COUNTER_PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'APPROVED',
      history: [
        {
          amount: 680,
          type: 'PROPOSED',
          status: 'SUBMITTED',
          timestamp: '2023-10-10T11:30:00Z',
          userId: 'user-001',
          message: 'Proposed 2024 rate with 4.6% increase'
        },
        {
          amount: 680,
          type: 'COUNTER_PROPOSED',
          status: 'APPROVED',
          timestamp: '2023-10-20T15:45:00Z',
          userId: 'user-014',
          message: 'Rate approved as proposed'
        }
      ],
      createdAt: '2023-10-10T11:30:00Z',
      updatedAt: '2023-10-20T15:45:00Z'
    },
    
    // Global Industries counter-proposals to XYZ Legal
    {
      id: 'counter-rate-003',
      attorneyId: 'attorney-005',
      clientId: 'client-002',
      firmId: 'firm-002',
      staffClassId: 'staffclass-005',
      officeId: 'office-003',
      amount: 748,
      currency: 'USD',
      type: 'COUNTER_PROPOSED',
      effectiveDate: '2024-01-01',
      expirationDate: '2024-12-31',
      status: 'UNDER_REVIEW',
      history: [
        {
          amount: 750,
          type: 'PROPOSED',
          status: 'SUBMITTED',
          timestamp: '2023-10-05T14:15:00Z',
          userId: 'user-005',
          message: 'Proposed 2024 rate with 4.2% increase'
        },
        {
          amount: 748,
          type: 'COUNTER_PROPOSED',
          status: 'UNDER_REVIEW',
          timestamp: '2023-10-18T11:30:00Z',
          userId: 'user-018',
          message: 'Minor adjustment to align with our budgeted increases'
        }
      ],
      createdAt: '2023-10-05T14:15:00Z',
      updatedAt: '2023-10-18T11:30:00Z'
    }
  ]
};

// Mock Negotiations
export const mockNegotiations = {
  active: [
    // ABC Law - Acme Corporation negotiation (in progress)
    {
      id: 'negotiation-001',
      type: 'RATE_SUBMISSION',
      status: 'CLIENT_COUNTERED',
      clientId: 'client-001',
      firmId: 'firm-001',
      client: mockOrganizations.clients[0],
      firm: mockOrganizations.lawFirms[0],
      requestDate: '2023-09-15',
      submissionDeadline: '2023-11-15',
      completionDate: '',
      messageThreadId: 'thread-001',
      rateIds: ['prop-rate-001', 'prop-rate-002', 'prop-rate-003'],
      approvalWorkflowId: 'workflow-001',
      approvalStatus: 'PENDING',
      createdBy: 'user-001',
      createdAt: '2023-09-15T14:30:00Z',
      updatedAt: '2023-10-20T15:45:00Z'
    },
    // XYZ Legal - Global Industries negotiation (in progress)
    {
      id: 'negotiation-002',
      type: 'RATE_SUBMISSION',
      status: 'CLIENT_COUNTERED',
      clientId: 'client-002',
      firmId: 'firm-002',
      client: mockOrganizations.clients[1],
      firm: mockOrganizations.lawFirms[1],
      requestDate: '2023-09-20',
      submissionDeadline: '2023-11-30',
      completionDate: '',
      messageThreadId: 'thread-002',
      rateIds: ['prop-rate-004', 'prop-rate-005'],
      approvalWorkflowId: 'workflow-002',
      approvalStatus: 'PENDING',
      createdBy: 'user-005',
      createdAt: '2023-09-20T10:15:00Z',
      updatedAt: '2023-10-18T11:30:00Z'
    },
    // Smith & Jones - Tech Innovations negotiation (not yet submitted)
    {
      id: 'negotiation-003',
      type: 'RATE_SUBMISSION',
      status: 'REQUESTED',
      clientId: 'client-003',
      firmId: 'firm-003',
      client: mockOrganizations.clients[2],
      firm: mockOrganizations.lawFirms[2],
      requestDate: '2023-10-01',
      submissionDeadline: '2023-12-15',
      completionDate: '',
      messageThreadId: 'thread-003',
      rateIds: ['prop-rate-006', 'prop-rate-007'],
      approvalWorkflowId: '',
      approvalStatus: 'PENDING',
      createdBy: 'user-021',
      createdAt: '2023-10-01T09:30:00Z',
      updatedAt: '2023-10-01T09:30:00Z'
    }
  ],
  
  completed: [
    // A completed negotiation from last year
    {
      id: 'negotiation-004',
      type: 'RATE_SUBMISSION',
      status: 'COMPLETED',
      clientId: 'client-001',
      firmId: 'firm-001',
      client: mockOrganizations.clients[0],
      firm: mockOrganizations.lawFirms[0],
      requestDate: '2022-09-10',
      submissionDeadline: '2022-11-30',
      completionDate: '2022-11-15',
      messageThreadId: 'thread-004',
      rateIds: ['rate-001', 'rate-002', 'rate-003'],
      approvalWorkflowId: 'workflow-003',
      approvalStatus: 'APPROVED',
      createdBy: 'user-001',
      createdAt: '2022-09-10T11:45:00Z',
      updatedAt: '2022-11-15T14:30:00Z'
    },
    // Another completed negotiation from last year
    {
      id: 'negotiation-005',
      type: 'RATE_SUBMISSION',
      status: 'COMPLETED',
      clientId: 'client-002',
      firmId: 'firm-002',
      client: mockOrganizations.clients[1],
      firm: mockOrganizations.lawFirms[1],
      requestDate: '2022-08-15',
      submissionDeadline: '2022-10-31',
      completionDate: '2022-10-20',
      messageThreadId: 'thread-005',
      rateIds: ['rate-004', 'rate-005'],
      approvalWorkflowId: 'workflow-004',
      approvalStatus: 'APPROVED',
      createdBy: 'user-005',
      createdAt: '2022-08-15T10:30:00Z',
      updatedAt: '2022-10-20T11:45:00Z'
    }
  ],
  
  requested: [
    // New request that hasn't been responded to yet
    {
      id: 'negotiation-006',
      type: 'RATE_SUBMISSION',
      status: 'REQUESTED',
      clientId: 'client-001',
      firmId: 'firm-003',
      client: mockOrganizations.clients[0],
      firm: mockOrganizations.lawFirms[2],
      requestDate: '2023-10-05',
      submissionDeadline: '',
      completionDate: '',
      messageThreadId: 'thread-006',
      rateIds: [],
      approvalWorkflowId: '',
      approvalStatus: 'PENDING',
      createdBy: 'user-009',
      createdAt: '2023-10-05T15:30:00Z',
      updatedAt: '2023-10-05T15:30:00Z'
    }
  ]
};

// Mock Messages
export const mockMessages = {
  threads: [
    // Thread for ABC Law - Acme Corporation negotiation
    {
      id: 'thread-001',
      title: 'ABC Law 2024 Rate Negotiation',
      participants: [
        mockUsers.lawFirmUsers[0], // John Smith
        mockUsers.lawFirmUsers[1], // Alice Green
        mockUsers.clientUsers[0], // Robert Chen
        mockUsers.clientUsers[1]  // Daniel Smith
      ],
      relatedEntityType: 'Negotiation',
      relatedEntityId: 'negotiation-001',
      messageCount: 4,
      unreadCount: 1,
      latestMessage: null, // Will be populated from messages array
      createdAt: '2023-09-15T14:30:00Z',
      updatedAt: '2023-10-20T15:45:00Z'
    },
    // Thread for XYZ Legal - Global Industries negotiation
    {
      id: 'thread-002',
      title: 'XYZ Legal 2024 Rate Negotiation',
      participants: [
        mockUsers.lawFirmUsers[4], // Sarah Johnson
        mockUsers.lawFirmUsers[5], // Tom Brown
        mockUsers.clientUsers[4], // Jessica Martinez
        mockUsers.clientUsers[5]  // Alex Kim
      ],
      relatedEntityType: 'Negotiation',
      relatedEntityId: 'negotiation-002',
      messageCount: 3,
      unreadCount: 0,
      latestMessage: null, // Will be populated from messages array
      createdAt: '2023-09-20T10:15:00Z',
      updatedAt: '2023-10-18T11:30:00Z'
    },
    // Thread for Smith & Jones - Tech Innovations negotiation
    {
      id: 'thread-003',
      title: 'Smith & Jones 2024 Rate Negotiation',
      participants: [
        mockUsers.lawFirmUsers[8],  // Michael Wilson
        mockUsers.lawFirmUsers[9],  // Kiran Patel
        mockUsers.clientUsers[8],   // David Wong
        mockUsers.clientUsers[9]    // Laura Rodriguez
      ],
      relatedEntityType: 'Negotiation',
      relatedEntityId: 'negotiation-003',
      messageCount: 2,
      unreadCount: 0,
      latestMessage: null, // Will be populated from messages array
      createdAt: '2023-10-01T09:30:00Z',
      updatedAt: '2023-10-10T14:15:00Z'
    }
  ],
  
  messages: [
    // Messages for ABC Law - Acme Corporation negotiation
    {
      id: 'message-001',
      threadId: 'thread-001',
      parentId: null,
      senderId: 'user-001', // John Smith
      sender: mockUsers.lawFirmUsers[0],
      recipientIds: ['user-013', 'user-014'], // Robert Chen, Daniel Smith
      content: 'We are pleased to submit our proposed rates for 2024. These rates reflect the high quality of service and expertise we provide to Acme Corporation.',
      attachments: [],
      relatedEntityType: 'Negotiation',
      relatedEntityId: 'negotiation-001',
      isRead: true,
      createdAt: '2023-10-10T11:30:00Z',
      updatedAt: '2023-10-10T11:30:00Z'
    },
    {
      id: 'message-002',
      threadId: 'thread-001',
      parentId: null,
      senderId: 'user-014', // Daniel Smith
      sender: mockUsers.clientUsers[1],
      recipientIds: ['user-001', 'user-002'], // John Smith, Alice Green
      content: 'Thank you for your submission. We will review the proposed rates and get back to you shortly.',
      attachments: [],
      relatedEntityType: 'Negotiation',
      relatedEntityId: 'negotiation-001',
      isRead: true,
      createdAt: '2023-10-12T09:45:00Z',
      updatedAt: '2023-10-12T09:45:00Z'
    },
    {
      id: 'message-003',
      threadId: 'thread-001',
      parentId: null,
      senderId: 'user-014', // Daniel Smith
      sender: mockUsers.clientUsers[1],
      recipientIds: ['user-001', 'user-002'], // John Smith, Alice Green
      content: 'We have reviewed your proposed rates for 2024. While most of the rates are acceptable, we have concerns about the increase for James Smith, which exceeds our 5% increase guideline. We have proposed a counter-rate of $787 which represents a 5% increase. Please review and let us know if this is acceptable.',
      attachments: [],
      relatedEntityType: 'Rate',
      relatedEntityId: 'prop-rate-001',
      isRead: true,
      createdAt: '2023-10-20T15:45:00Z',
      updatedAt: '2023-10-20T15:45:00Z'
    },
    {
      id: 'message-004',
      threadId: 'thread-001',
      parentId: 'message-003',
      senderId: 'user-001', // John Smith
      sender: mockUsers.lawFirmUsers[0],
      recipientIds: ['user-013', 'user-014'], // Robert Chen, Daniel Smith
      content: 'Thank you for your counter-proposal. We understand your concerns about the increase percentage. Mr. Smith has taken on additional responsibilities for Acme matters this year, but we appreciate working within your guidelines. We accept your counter-proposal of $787.',
      attachments: [],
      relatedEntityType: 'Rate',
      relatedEntityId: 'prop-rate-001',
      isRead: false,
      createdAt: '2023-10-21T10:30:00Z',
      updatedAt: '2023-10-21T10:30:00Z'
    },
    
    // Messages for XYZ Legal - Global Industries negotiation
    {
      id: 'message-005',
      threadId: 'thread-002',
      parentId: null,
      senderId: 'user-005', // Sarah Johnson
      sender: mockUsers.lawFirmUsers[4],
      recipientIds: ['user-017', 'user-018'], // Jessica Martinez, Alex Kim
      content: 'Please find our proposed rates for 2024. These rates reflect market conditions and the specialized expertise our team brings to Global Industries matters.',
      attachments: [],
      relatedEntityType: 'Negotiation',
      relatedEntityId: 'negotiation-002',
      isRead: true,
      createdAt: '2023-10-05T14:15:00Z',
      updatedAt: '2023-10-05T14:15:00Z'
    },
    {
      id: 'message-006',
      threadId: 'thread-002',
      parentId: null,
      senderId: 'user-018', // Alex Kim
      sender: mockUsers.clientUsers[5],
      recipientIds: ['user-005', 'user-006'], // Sarah Johnson, Tom Brown
      content: 'Thank you for your submission. We have reviewed the proposed rates and have a minor adjustment to Robert Johnson\'s rate to align with our budgeted increases. Please see our counter-proposal.',
      attachments: [],
      relatedEntityType: 'Rate',
      relatedEntityId: 'prop-rate-004',
      isRead: true,
      createdAt: '2023-10-18T11:30:00Z',
      updatedAt: '2023-10-18T11:30:00Z'
    },
    {
      id: 'message-007',
      threadId: 'thread-002',
      parentId: 'message-006',
      senderId: 'user-005', // Sarah Johnson
      sender: mockUsers.lawFirmUsers[4],
      recipientIds: ['user-017', 'user-018'], // Jessica Martinez, Alex Kim
      content: 'We accept your counter-proposal of $748 for Robert Johnson. Thank you for your prompt review and feedback.',
      attachments: [],
      relatedEntityType: 'Rate',
      relatedEntityId: 'prop-rate-004',
      isRead: true,
      createdAt: '2023-10-19T09:45:00Z',
      updatedAt: '2023-10-19T09:45:00Z'
    },
    
    // Messages for Smith & Jones - Tech Innovations negotiation
    {
      id: 'message-008',
      threadId: 'thread-003',
      parentId: null,
      senderId: 'user-021', // David Wong
      sender: mockUsers.clientUsers[8],
      recipientIds: ['user-009', 'user-010'], // Michael Wilson, Kiran Patel
      content: 'We would like to invite Smith & Jones to submit your proposed rates for 2024. Please prepare your submission by December 15, 2023.',
      attachments: [],
      relatedEntityType: 'Negotiation',
      relatedEntityId: 'negotiation-003',
      isRead: true,
      createdAt: '2023-10-01T09:30:00Z',
      updatedAt: '2023-10-01T09:30:00Z'
    },
    {
      id: 'message-009',
      threadId: 'thread-003',
      parentId: 'message-008',
      senderId: 'user-009', // Michael Wilson
      sender: mockUsers.lawFirmUsers[8],
      recipientIds: ['user-021', 'user-022'], // David Wong, Laura Rodriguez
      content: 'Thank you for the invitation. We are working on our 2024 rates and will submit them well before the deadline. We appreciate the continued relationship with Tech Innovations.',
      attachments: [],
      relatedEntityType: 'Negotiation',
      relatedEntityId: 'negotiation-003',
      isRead: true,
      createdAt: '2023-10-10T14:15:00Z',
      updatedAt: '2023-10-10T14:15:00Z'
    }
  ]
};

// Populate latestMessage in threads
mockMessages.threads[0].latestMessage = mockMessages.messages[3];
mockMessages.threads[1].latestMessage = mockMessages.messages[6];
mockMessages.threads[2].latestMessage = mockMessages.messages[8];

// Mock Outside Counsel Guidelines (OCGs)
export const mockOCGs = [
  {
    id: 'ocg-001',
    title: 'Acme Corporation 2024 Outside Counsel Guidelines',
    version: 2.0,
    status: 'Published',
    clientId: 'client-001',
    client: mockOrganizations.clients[0],
    sections: [
      {
        id: 'section-001',
        title: 'Introduction',
        content: 'These guidelines outline Acme Corporation\'s expectations for outside counsel and billing practices.',
        isNegotiable: false,
        alternatives: [],
        order: 1
      },
      {
        id: 'section-002',
        title: 'Rate Structure',
        content: 'Rates will be frozen for 24 months from the effective date.',
        isNegotiable: true,
        alternatives: [
          {
            id: 'alt-001',
            title: 'Standard',
            content: 'Rates will be frozen for 24 months from the effective date.',
            points: 0,
            isDefault: true
          },
          {
            id: 'alt-002',
            title: 'Flexible',
            content: 'Rates will be frozen for 12 months from the effective date.',
            points: 3,
            isDefault: false
          }
        ],
        order: 2
      },
      {
        id: 'section-003',
        title: 'Billing Guidelines',
        content: 'Invoices must be submitted monthly and include detailed time entries.',
        isNegotiable: true,
        alternatives: [
          {
            id: 'alt-003',
            title: 'Standard',
            content: 'Invoices must be submitted monthly and include detailed time entries.',
            points: 0,
            isDefault: true
          },
          {
            id: 'alt-004',
            title: 'Flexible',
            content: 'Invoices must be submitted quarterly and include detailed time entries.',
            points: 2,
            isDefault: false
          }
        ],
        order: 3
      },
      {
        id: 'section-004',
        title: 'Staffing Requirements',
        content: 'Client approval required for all new timekeepers assigned to matters.',
        isNegotiable: true,
        alternatives: [
          {
            id: 'alt-005',
            title: 'Standard',
            content: 'Client approval required for all new timekeepers assigned to matters.',
            points: 0,
            isDefault: true
          },
          {
            id: 'alt-006',
            title: 'Flexible',
            content: 'Client approval required only for partner-level timekeepers assigned to matters.',
            points: 2,
            isDefault: false
          }
        ],
        order: 4
      }
    ],
    totalPoints: 7,
    createdAt: new Date('2023-08-15'),
    updatedAt: new Date('2023-09-01')
  },
  {
    id: 'ocg-002',
    title: 'Global Industries Outside Counsel Guidelines',
    version: 3.0,
    status: 'Published',
    clientId: 'client-002',
    client: mockOrganizations.clients[1],
    sections: [
      {
        id: 'section-005',
        title: 'Introduction',
        content: 'These guidelines establish the working relationship between Global Industries and its outside counsel.',
        isNegotiable: false,
        alternatives: [],
        order: 1
      },
      {
        id: 'section-006',
        title: 'Alternative Fee Arrangements',
        content: 'Global Industries requires that 65% of matters be billed under AFAs.',
        isNegotiable: true,
        alternatives: [
          {
            id: 'alt-007',
            title: 'Standard',
            content: 'Global Industries requires that 65% of matters be billed under AFAs.',
            points: 0,
            isDefault: true
          },
          {
            id: 'alt-008',
            title: 'Moderate',
            content: 'Global Industries requires that 50% of matters be billed under AFAs.',
            points: 2,
            isDefault: false
          },
          {
            id: 'alt-009',
            title: 'Minimal',
            content: 'Global Industries requires that 35% of matters be billed under AFAs.',
            points: 4,
            isDefault: false
          }
        ],
        order: 2
      },
      {
        id: 'section-007',
        title: 'Rate Reviews',
        content: 'Rate negotiations will be conducted annually during September-November.',
        isNegotiable: true,
        alternatives: [
          {
            id: 'alt-010',
            title: 'Standard',
            content: 'Rate negotiations will be conducted annually during September-November.',
            points: 0,
            isDefault: true
          },
          {
            id: 'alt-011',
            title: 'Flexible',
            content: 'Rate negotiations will be conducted annually with timing to be mutually agreed upon.',
            points: 1,
            isDefault: false
          }
        ],
        order: 3
      }
    ],
    totalPoints: 5,
    createdAt: new Date('2023-07-10'),
    updatedAt: new Date('2023-07-25')
  },
  {
    id: 'ocg-003',
    title: 'Tech Innovations Legal Vendor Guidelines',
    version: 1.0,
    status: 'Draft',
    clientId: 'client-003',
    client: mockOrganizations.clients[2],
    sections: [
      {
        id: 'section-008',
        title: 'Introduction',
        content: 'These guidelines outline the expectations for legal service providers working with Tech Innovations.',
        isNegotiable: false,
        alternatives: [],
        order: 1
      },
      {
        id: 'section-009',
        title: 'Diversity Requirements',
        content: 'Law firms must staff matters with at least 40% diverse attorneys.',
        isNegotiable: true,
        alternatives: [
          {
            id: 'alt-012',
            title: 'Standard',
            content: 'Law firms must staff matters with at least 40% diverse attorneys.',
            points: 0,
            isDefault: true
          },
          {
            id: 'alt-013',
            title: 'Modified',
            content: 'Law firms must staff matters with at least 30% diverse attorneys.',
            points: 2,
            isDefault: false
          }
        ],
        order: 2
      },
      {
        id: 'section-010',
        title: 'Technology Requirements',
        content: 'Law firms must use compatible e-billing and matter management platforms.',
        isNegotiable: true,
        alternatives: [
          {
            id: 'alt-014',
            title: 'Standard',
            content: 'Law firms must use compatible e-billing and matter management platforms.',
            points: 0,
            isDefault: true
          },
          {
            id: 'alt-015',
            title: 'Modified',
            content: 'Law firms may use their own systems with API integration capabilities.',
            points: 2,
            isDefault: false
          }
        ],
        order: 3
      }
    ],
    totalPoints: 4,
    createdAt: new Date('2023-09-20'),
    updatedAt: new Date('2023-09-20')
  }
];

// Mock Peer Groups
export const mockPeerGroups = [
  {
    id: 'peergroup-001',
    name: 'AmLaw 100',
    description: 'Top 100 US law firms by revenue',
    members: ['firm-001', 'firm-002', 'firm-003'],
    createdAt: new Date('2023-01-15'),
    updatedAt: new Date('2023-01-15')
  },
  {
    id: 'peergroup-002',
    name: 'IP Specialists',
    description: 'Firms specializing in intellectual property',
    members: ['firm-002'],
    createdAt: new Date('2023-01-15'),
    updatedAt: new Date('2023-01-15')
  },
  {
    id: 'peergroup-003',
    name: 'Employment Law Firms',
    description: 'Firms specializing in employment and labor law',
    members: ['firm-003'],
    createdAt: new Date('2023-01-15'),
    updatedAt: new Date('2023-01-15')
  },
  {
    id: 'peergroup-004',
    name: 'Fortune 500 Clients',
    description: 'Fortune 500 companies',
    members: ['client-001', 'client-002'],
    createdAt: new Date('2023-01-15'),
    updatedAt: new Date('2023-01-15')
  },
  {
    id: 'peergroup-005',
    name: 'Tech Industry Clients',
    description: 'Technology industry clients',
    members: ['client-003'],
    createdAt: new Date('2023-01-15'),
    updatedAt: new Date('2023-01-15')
  }
];

// Mock Analytics Data
export const mockAnalyticsData = {
  rateImpact: {
    totalCurrentAmount: 2500000,
    totalProposedAmount: 2602500,
    totalImpact: 102500,
    percentageChange: 4.1,
    currency: 'USD',
    items: [
      {
        label: 'ABC Law LLP',
        id: 'firm-001',
        currentAmount: 950000,
        proposedAmount: 989750,
        impact: 39750,
        percentageChange: 4.2,
        hoursLastYear: 3550
      },
      {
        label: 'XYZ Legal Group',
        id: 'firm-002',
        currentAmount: 870000,
        proposedAmount: 905850,
        impact: 35850,
        percentageChange: 4.1,
        hoursLastYear: 3250
      },
      {
        label: 'Smith & Jones LLP',
        id: 'firm-003',
        currentAmount: 680000,
        proposedAmount: 706900,
        impact: 26900,
        percentageChange: 3.2,
        hoursLastYear: 2800
      }
    ],
    highestImpact: {
      label: 'ABC Law LLP',
      id: 'firm-001',
      currentAmount: 950000,
      proposedAmount: 989750,
      impact: 39750,
      percentageChange: 4.2,
      hoursLastYear: 3550
    },
    lowestImpact: {
      label: 'Smith & Jones LLP',
      id: 'firm-003',
      currentAmount: 680000,
      proposedAmount: 706900,
      impact: 26900,
      percentageChange: 3.2,
      hoursLastYear: 2800
    },
    dimension: 'FIRM',
    peerComparison: {
      averageIncrease: 3.9,
      rangeMin: 3.0,
      rangeMax: 4.8
    },
    multiYearProjection: [
      { year: 2023, amount: 2500000 },
      { year: 2024, amount: 2602500 },
      { year: 2025, amount: 2706600 },
      { year: 2026, amount: 2814864 },
      { year: 2027, amount: 2927459 }
    ]
  },
  
  peerComparison: {
    peerGroup: {
      id: 'peergroup-001',
      name: 'AmLaw 100',
      averageRateIncrease: 3.9,
      minRateIncrease: 3.0,
      maxRateIncrease: 4.8,
      percentile25: 3.4,
      percentile50: 3.9,
      percentile75: 4.3,
      averageRate: 675,
      currency: 'USD',
      memberCount: 100
    },
    items: [
      {
        id: 'firm-001',
        name: 'ABC Law LLP',
        rateIncrease: 4.2,
        rateAmount: 725,
        currency: 'USD',
        percentile: 65,
        dimension: 'FIRM'
      },
      {
        id: 'firm-002',
        name: 'XYZ Legal Group',
        rateIncrease: 4.1,
        rateAmount: 685,
        currency: 'USD',
        percentile: 60,
        dimension: 'FIRM'
      },
      {
        id: 'firm-003',
        name: 'Smith & Jones LLP',
        rateIncrease: 3.2,
        rateAmount: 615,
        currency: 'USD',
        percentile: 35,
        dimension: 'FIRM'
      }
    ],
    yourAverage: 4.1,
    yourPercentile: 60,
    dimension: 'FIRM',
    trends: [
      { year: 2019, yourAverage: 3.1, peerAverage: 3.2 },
      { year: 2020, yourAverage: 2.8, peerAverage: 2.5 },
      { year: 2021, yourAverage: 2.9, peerAverage: 3.0 },
      { year: 2022, yourAverage: 3.8, peerAverage: 3.5 },
      { year: 2023, yourAverage: 4.1, peerAverage: 3.9 }
    ]
  },
  
  historicalTrends: {
    series: [
      {
        id: 'firm-001',
        name: 'ABC Law LLP',
        data: [
          { year: 2019, value: 3.2, percentChange: null },
          { year: 2020, value: 2.9, percentChange: -9.4 },
          { year: 2021, value: 3.1, percentChange: 6.9 },
          { year: 2022, value: 3.7, percentChange: 19.4 },
          { year: 2023, value: 4.2, percentChange: 13.5 }
        ],
        cagr: 7.0,
        dimension: 'FIRM'
      },
      {
        id: 'firm-002',
        name: 'XYZ Legal Group',
        data: [
          { year: 2019, value: 3.0, percentChange: null },
          { year: 2020, value: 2.5, percentChange: -16.7 },
          { year: 2021, value: 2.8, percentChange: 12.0 },
          { year: 2022, value: 3.5, percentChange: 25.0 },
          { year: 2023, value: 4.1, percentChange: 17.1 }
        ],
        cagr: 8.1,
        dimension: 'FIRM'
      },
      {
        id: 'firm-003',
        name: 'Smith & Jones LLP',
        data: [
          { year: 2019, value: 3.1, percentChange: null },
          { year: 2020, value: 2.2, percentChange: -29.0 },
          { year: 2021, value: 2.8, percentChange: 27.3 },
          { year: 2022, value: 3.0, percentChange: 7.1 },
          { year: 2023, value: 3.2, percentChange: 6.7 }
        ],
        cagr: 0.8,
        dimension: 'FIRM'
      }
    ],
    overallCagr: 5.3,
    inflationData: [
      { year: 2019, value: 2.3, percentChange: null },
      { year: 2020, value: 1.4, percentChange: -39.1 },
      { year: 2021, value: 7.0, percentChange: 400.0 },
      { year: 2022, value: 6.5, percentChange: -7.1 },
      { year: 2023, value: 3.2, percentChange: -50.8 }
    ],
    metricType: 'RATE_INCREASE',
    currency: 'USD',
    dimension: 'FIRM'
  },
  
  attorneyPerformance: {
    attorneyId: 'attorney-001',
    attorneyName: 'James Smith',
    metrics: [
      {
        type: 'HOURS',
        value: 1850,
        label: 'Hours Billed',
        trend: 5.7,
        percentile: 85,
        historicalData: [
          { year: 2019, value: 1720 },
          { year: 2020, value: 1650 },
          { year: 2021, value: 1780 },
          { year: 2022, value: 1850 }
        ]
      },
      {
        type: 'MATTERS',
        value: 12,
        label: 'Matters Worked',
        trend: 0,
        percentile: 75,
        historicalData: [
          { year: 2019, value: 10 },
          { year: 2020, value: 11 },
          { year: 2021, value: 12 },
          { year: 2022, value: 12 }
        ]
      },
      {
        type: 'CLIENT_RATING',
        value: 4.5,
        label: 'Client Rating',
        trend: 0.2,
        percentile: 80,
        historicalData: [
          { year: 2019, value: 4.2 },
          { year: 2020, value: 4.3 },
          { year: 2021, value: 4.3 },
          { year: 2022, value: 4.5 }
        ]
      },
      {
        type: 'UNICOURT_PERFORMANCE',
        value: 85,
        label: 'UniCourt Percentile',
        trend: 5,
        percentile: 85,
        historicalData: [
          { year: 2019, value: 75 },
          { year: 2020, value: 78 },
          { year: 2021, value: 80 },
          { year: 2022, value: 85 }
        ]
      },
      {
        type: 'EFFICIENCY',
        value: 0.95,
        label: 'Efficiency',
        trend: 0.03,
        percentile: 90,
        historicalData: [
          { year: 2019, value: 0.89 },
          { year: 2020, value: 0.91 },
          { year: 2021, value: 0.92 },
          { year: 2022, value: 0.95 }
        ]
      }
    ],
    unicourtData: {
      caseCount: 87,
      winRate: 0.76,
      averageCaseDuration: 14.5,
      practiceAreaDistribution: [
        { area: 'Commercial', percentage: 51.7 },
        { area: 'IP', percentage: 25.3 },
        { area: 'Employment', percentage: 23.0 }
      ],
      courtExperience: [
        { court: 'SDNY', caseCount: 40 },
        { court: 'EDNY', caseCount: 25 },
        { court: 'DNJ', caseCount: 22 }
      ],
      overallPercentile: 85
    },
    staffClass: 'Partner',
    practiceArea: 'Litigation',
    overallRating: 4.7,
    currentRate: {
      amount: 750,
      currency: 'USD'
    }
  }
};

// Mock Integration Data
export const mockIntegrationData = {
  ebillingSystems: [
    {
      id: 'ebs-001',
      name: 'TeamConnect',
      type: 'TEAM_CONNECT',
      status: 'Configured',
      connectionDetails: {
        baseUrl: 'https://api.teamconnect.example.com',
        authenticationType: 'OAuth2.0',
        clientId: 'client_12345',
        clientSecret: '••••••••••••••••••••••••••'
      },
      lastSyncDate: '2023-09-01T14:30:00Z',
      nextSyncDate: '2023-10-01T14:30:00Z'
    },
    {
      id: 'ebs-002',
      name: 'Legal Tracker',
      type: 'LEGAL_TRACKER',
      status: 'Not Configured',
      connectionDetails: null,
      lastSyncDate: null,
      nextSyncDate: null
    },
    {
      id: 'ebs-003',
      name: 'Onit',
      type: 'ONIT',
      status: 'Not Configured',
      connectionDetails: null,
      lastSyncDate: null,
      nextSyncDate: null
    },
    {
      id: 'ebs-004',
      name: 'BrightFlag',
      type: 'BRIGHT_FLAG',
      status: 'Not Configured',
      connectionDetails: null,
      lastSyncDate: null,
      nextSyncDate: null
    }
  ],
  
  fieldMappings: {
    import: {
      'timekeeper_id': 'Attorney.timekeeperIds',
      'timekeeper_name': 'Attorney.name',
      'vendor_id': 'Organization.id',
      'vendor_name': 'Organization.name',
      'rate_amount': 'Rate.amount',
      'rate_currency': 'Rate.currency',
      'effective_date': 'Rate.effectiveDate',
      'expiration_date': 'Rate.expirationDate',
      'practice_area': 'Attorney.practiceAreas',
      'office_location': 'Office.name'
    },
    export: {
      'Attorney.timekeeperIds': 'timekeeper_id',
      'Attorney.name': 'timekeeper_name',
      'Rate.amount': 'rate_amount',
      'Rate.currency': 'rate_currency',
      'Rate.effectiveDate': 'effective_date',
      'Rate.expirationDate': 'expiration_date'
    }
  },
  
  importResults: {
    lastImport: {
      date: '2023-09-01T14:30:00Z',
      status: 'Completed',
      recordsProcessed: 1250,
      recordsImported: 1240,
      errors: 10,
      duration: '00:05:43'
    },
    importHistory: [
      {
        date: '2023-09-01T14:30:00Z',
        status: 'Completed',
        recordsProcessed: 1250,
        recordsImported: 1240,
        errors: 10,
        duration: '00:05:43'
      },
      {
        date: '2023-08-01T14:30:00Z',
        status: 'Completed',
        recordsProcessed: 1230,
        recordsImported: 1225,
        errors: 5,
        duration: '00:05:22'
      },
      {
        date: '2023-07-01T14:30:00Z',
        status: 'Completed',
        recordsProcessed: 1210,
        recordsImported: 1205,
        errors: 5,
        duration: '00:05:15'
      }
    ]
  }
};

// Mock AI Recommendations
export const mockAIRecommendations = {
  rateRecommendations: [
    {
      rateId: 'prop-rate-001',
      attorneyId: 'attorney-001',
      currentRate: 750,
      proposedRate: 795,
      recommendedAction: 'counter',
      recommendedRate: 787,
      confidence: 0.85,
      rationale: 'The proposed increase of 6% exceeds the client\'s maximum increase guideline of 5%. Recommending a counter-proposal of $787, which represents a 5% increase and aligns with the client\'s guidelines while recognizing the attorney\'s strong performance metrics and high client rating.'
    },
    {
      rateId: 'prop-rate-002',
      attorneyId: 'attorney-002',
      currentRate: 650,
      proposedRate: 680,
      recommendedAction: 'approve',
      recommendedRate: 680,
      confidence: 0.92,
      rationale: 'The proposed increase of 4.6% is within the client\'s guidelines. Attorney shows excellent performance metrics and client ratings. Rate is competitive with peer group benchmarks.'
    },
    {
      rateId: 'prop-rate-003',
      attorneyId: 'attorney-003',
      currentRate: 550,
      proposedRate: 575,
      recommendedAction: 'counter',
      recommendedRate: 565,
      confidence: 0.78,
      rationale: 'While the proposed increase of 4.5% is within guidelines, recommending a slightly lower counter-proposal based on performance metrics that are good but not exceptional compared to peers in the same staff class.'
    },
    {
      rateId: 'prop-rate-004',
      attorneyId: 'attorney-005',
      currentRate: 720,
      proposedRate: 750,
      recommendedAction: 'counter',
      recommendedRate: 748,
      confidence: 0.81,
      rationale: 'The proposed increase is within guidelines, but recommending a minor adjustment to align with budgeted increases and maintain consistency across the firm\'s partner rates.'
    },
    {
      rateId: 'prop-rate-005',
      attorneyId: 'attorney-006',
      currentRate: 650,
      proposedRate: 675,
      recommendedAction: 'approve',
      recommendedRate: 675,
      confidence: 0.89,
      rationale: 'The proposed increase of 3.8% is below the maximum guideline and aligns with the attorney\'s performance and expertise in a specialized practice area. Rate is competitive with market benchmarks.'
    }
  ],
  
  chatResponses: [
    {
      query: 'How do our proposed rates compare to peer firms in the AmLaw 100 group?',
      response: 'Based on your current negotiations, your proposed rates show an average increase of 4.1% compared to the AmLaw 100 peer group average of 3.9%. You\'re within the peer range of 3.0% - 4.8%, but slightly above the average.\n\nThe highest increases are from ABC Law (4.2%) and XYZ Legal (4.1%), while Smith & Jones has the lowest at 3.2%.\n\nWould you like to see a breakdown by staff class or specific recommendations for counter-proposals?',
      contentType: 'text'
    },
    {
      query: 'Show me counter-proposal recommendations for ABC Law\'s partner rates.',
      response: {
        text: 'Here are my recommendations for ABC Law partner rates:',
        table: {
          headers: ['Partner', 'Current', 'Proposed', 'Recommended', 'Reason'],
          rows: [
            ['J. Smith', '$750', '$795', '$787', 'High perf'],
            ['A. Jones', '$650', '$680', '$670', 'Avg perf']
          ]
        },
        followUp: 'Would you like me to apply these recommendations to your current negotiation with ABC Law?'
      },
      contentType: 'richText'
    },
    {
      query: 'What would be the total financial impact of accepting all proposed rates versus counter-proposals?',
      response: {
        text: 'Here\'s the financial impact analysis:',
        chart: {
          type: 'bar',
          data: {
            labels: ['Proposed Rates', 'Counter-Proposed Rates'],
            datasets: [
              {
                label: 'Total Impact',
                data: [102500, 92250]
              }
            ]
          }
        },
        summary: 'Accepting all proposed rates would have a financial impact of $102,500 (4.1% increase).\nImplementing all recommended counter-proposals would reduce the impact to $92,250 (3.7% increase).\nThis represents a savings of $10,250 compared to the proposed rates.',
        breakdown: 'By firm: ABC Law ($39,750 → $35,775), XYZ Legal ($35,850 → $33,350), Smith & Jones ($26,900 → $23,125)'
      },
      contentType: 'richText'
    }
  ]
};