export const extractErrorMessage = (error: any): string => {
  if (error.response?.data?.detail) {
    if (Array.isArray(error.response.data.detail)) {
      return error.response.data.detail
        .map((e: any) => `${e.loc.join(".")}: ${e.msg}`)
        .join(", ");
    } else if (typeof error.response.data.detail === "string") {
      return error.response.data.detail;
    }
  }
  return error.message || "エラーが発生しました";
};

