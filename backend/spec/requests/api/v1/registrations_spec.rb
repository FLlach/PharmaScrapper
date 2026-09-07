require 'swagger_helper'

RSpec.describe 'api/v1/registrations', type: :request do
  path '/api/v1/registrations' do
    post('create user') do
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
        let(:user) { { email_address: 'test@example.com', password: 'password123', password_confirmation: 'password123', name: 'Test User' } }

        schema type: :object, properties: {
          message: { type: :string },
          user: {
            type: :object,
            properties: {
              id: { type: :integer },
              email: { type: :string },
              name: { type: :string, nullable: true },
              role: { type: :string }
            }
          }
        }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['message']).to eq('User registered successfully')
          expect(data['user']['email']).to eq('test@example.com')
        end
      end

      response(422, 'unprocessable entity') do
        let(:user) { { email_address: '', password: 'password123', password_confirmation: 'password123', name: 'Test User' } }

        schema type: :object, properties: {
          errors: {
            type: :array,
            items: { type: :string }
          }
        }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data).to have_key('errors')
        end
      end
    end
  end
end
