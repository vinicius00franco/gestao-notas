import Constants from 'expo-constants';
import * as realJobService from '../api/services/jobService';
import * as realDashboardService from '../api/services/dashboardService';
import * as realContasService from '../api/services/contasService';
import * as realUnclassifiedCompaniesService from '../services/unclassifiedCompaniesService';
import * as realNotaFiscalService from '../services/notaFiscalService';
import * as realCalendarService from '../api/services/calendarService';

import * as mockServices from './MockDataProvider';

const appMode = Constants.expoConfig?.extra?.appMode || 'real';

export const JobService = appMode === 'mock' ? mockServices.MockJobService : realJobService;
export const DashboardService = appMode === 'mock' ? mockServices.MockDashboardService : realDashboardService;
export const ContasService = appMode === 'mock' ? mockServices.MockContasService : realContasService;
export const UnclassifiedCompaniesService = appMode === 'mock' ? mockServices.MockUnclassifiedCompaniesService : realUnclassifiedCompaniesService;
export const NotaFiscalService = appMode === 'mock' ? mockServices.MockNotaFiscalService : realNotaFiscalService;
export const CalendarService = appMode === 'mock' ? mockServices.MockCalendarService : realCalendarService;
