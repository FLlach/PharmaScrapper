require 'swagger_helper'

RSpec.describe 'api/v1/registrations', type: :request do
  path '/api/v1/registrations' do
    post('create registration') do
      tags 'Registrations'
      consumes 'application/json'
      produces 'application/json'
      parameter name: :user, in: :body, schema: {
        type: :object,
        properties: {
          email_address: { type: :string },
          password: { type: :string },
          password_confirmation: { type: :string },
          name: { type: :string }
        },
        required: [ 'email_address', 'password', 'password_confirmation' ]
      }

      response(201, 'created') do
        schema type: :object, properties: {
          message: { type: :string },
          user: {
            type: :object,
            properties: {
              id: { type: :integer },
              email: { type: :string },
              name: { type: :string, nullable: true },
              role: { type: :string }
            },
            required: [ 'id', 'email', 'role' ]
          }
        }, required: [ 'message', 'user' ]

        let(:user) { { email_address: 'test@example.com', password: 'password123', password_confirmation: 'password123', name: 'Test User' } }

        run_test!
      end

      response(422, 'unprocessable entity') do
        schema type: :object, properties: {
          errors: {
            type: :array,
            items: { type: :string }
          }
        }, required: [ 'errors' ]

        let(:user) { { email_address: 'test@example.com', password: 'password123', password_confirmation: 'wrong_password' } }

        run_test!
      end
    end
  end
end
