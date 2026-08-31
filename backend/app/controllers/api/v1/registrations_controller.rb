module Api
  module V1
    class RegistrationsController < ApplicationController
      allow_unauthenticated_access only: [:create]

      def create
        user = User.new(user_params)

        if user.save
          render json: { message: "User registered successfully", user: { id: user.id, email: user.email_address, name: user.name, role: user.role } }, status: :created
        else
          render json: { errors: user.errors.full_messages }, status: :unprocessable_entity
        end
      end

      private

      def user_params
        params.permit(:email_address, :password, :password_confirmation, :name)
      end
    end
  end
end
