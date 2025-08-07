import axios from 'axios';

export default {
  data() {
    return {
      abortController: null,
    };
  },
  methods: {
    makeRequest(url) {
      if (this.abortController) {
        this.abortController.abort();
      }
      this.abortController = new AbortController();
      const request = axios.get(url, {
        signal: this.abortController.signal,
      });
      return {
        then(responseHandler) {
          request.then(
            (response) => {
              responseHandler.call(null, response);
            },
            (error) => {
              // catch cancelations to prevent sending them to sentry as errors
              if (!axios.isCancel(error)) {
                throw error;
              }
            },
          );
        },
      };
    },
  },
};
