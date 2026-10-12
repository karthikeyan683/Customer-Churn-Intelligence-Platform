import api from "./axios";

export const getAnalyticsSummary = async () => {
const response = await api.get("/analytics/summary");
return response.data;
};

export const getRiskDistribution = async () => {
const response = await api.get("/analytics/risk-distribution");
return response.data;
};

export const getChurnByContract = async () => {
const response = await api.get("/analytics/churn-by-contract");
return response.data;
};

export const getHighRiskCustomers = async () => {
const response = await api.get("/analytics/high-risk-customers");
return response.data;
};
