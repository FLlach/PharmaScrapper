module Api
  module V1
    class PharmaciesController < ApplicationController
      allow_unauthenticated_access only: [:index]

      def index
        render json: Pharmacy.all
      end
    end
  end
end
