module Api
  module V1
    class MedicinesController < ApplicationController
      def index
        # GET /api/v1/medicines?query=paracetamol
      end

      def comparison
        # GET /api/v1/medicines/:id/comparison
      end
    end
  end
end
