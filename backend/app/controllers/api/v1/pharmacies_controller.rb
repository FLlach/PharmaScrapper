module Api
  module V1
    class PharmaciesController < ApplicationController
      allow_unauthenticated_access only: [:index]

      def index
        pharmacies = Pharmacy.all
        render json: pharmacies, status: :ok
      end
    end
  end
end
